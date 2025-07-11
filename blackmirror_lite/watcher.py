import os
import sys
import time
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .store import MirrorStore
from fnmatch import fnmatch
import shutil
import urllib.request
import urllib.parse
import threading
import hashlib

# configure simple console logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_ignore_patterns(base_path):
    """Load default and .bmlignore patterns for a watched directory."""
    # Default ignores: Git metadata, env files, bmlignore, and common build/cache dirs
    patterns = ['.git', '.env', '.bmlignore', 'env', 'venv', 'logs', 'node_modules']
    # Scan for .bmlignore and .gitignore files throughout the tree
    for root, _, files in os.walk(base_path):
        rel_dir = os.path.relpath(root, base_path)
        for ig in ('.bmlignore', '.gitignore'):
            if ig in files:
                path = os.path.join(root, ig)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        for line in f:
                            p = line.strip()
                            if not p or p.startswith('#'):
                                continue
                            # Prefix nested ignore rules with relative directory
                            if rel_dir not in ('.', os.curdir):
                                patterns.append(os.path.join(rel_dir, p))
                            patterns.append(p)
                except Exception:
                    continue
    return patterns


def auto_bootstrap_ignore(base_path):
    """Ensure a .bmlignore exists: copy .gitignore or fetch templates based on project type."""
    gitignore = os.path.join(base_path, '.gitignore')
    bmlignore = os.path.join(base_path, '.bmlignore')
    if os.path.exists(bmlignore):
        return
    if os.path.exists(gitignore):
        try:
            shutil.copyfile(gitignore, bmlignore)
            logger.info(f"Copied .gitignore to .bmlignore in {base_path}")
        except Exception as e:
            logger.warning(f"Failed to copy .gitignore: {e}")
        return
    # No ignore file: detect simple languages and optionally fetch templates
    if not sys.stdin.isatty():
        return
    # Map file extensions to GitHub gitignore template names
    ext_map = {'py': 'Python', 'js': 'Node', 'java': 'Java', 'go': 'Go',
               'rs': 'Rust', 'cpp': 'C++', 'cs': 'CSharp'}
    langs = set()
    for root, dirs, files in os.walk(base_path):
        for fn in files:
            ext = os.path.splitext(fn)[1].lstrip('.').lower()
            if ext in ext_map:
                langs.add(ext_map[ext])
        break
    if not langs:
        return
    prompt = (
        f"No .bmlignore or .gitignore found in {base_path}. "
        f"Detected project types: {', '.join(langs)}. "
        "Bootstrap .bmlignore with standard gitignore templates? [Y/n] "
    )
    resp = input(prompt)
    if resp and not resp.lower().startswith('y'):
        return
    entries = []
    for lang in langs:
        url = f"https://raw.githubusercontent.com/github/gitignore/main/{lang}.gitignore"
        try:
            with urllib.request.urlopen(url) as r:
                tmpl = r.read().decode('utf-8')
            entries.append(f"# {lang} patterns\n{tmpl}")
        except Exception as e:
            logger.warning(f"Failed to fetch .gitignore template for {lang}: {e}")
    if entries:
        try:
            with open(bmlignore, 'w', encoding='utf-8') as f:
                f.write('\n'.join(entries))
            logger.info(f"Created .bmlignore in {base_path} with templates: {', '.join(langs)}")
        except Exception as e:
            logger.warning(f"Failed to write .bmlignore: {e}")


def ingest_tree(base_path, store, force=False):
    """Traverse base_path, snapshot existing files that have no prior entries.

    If force=True, snapshot all files regardless of existing logs.
    """
    patterns = load_ignore_patterns(base_path)
    for root, dirs, files in os.walk(base_path):
        rel_root = os.path.relpath(root, base_path)
        # Skip ignored directories entirely
        skip_dir = False
        for pat in patterns:
            if fnmatch(rel_root, pat) or rel_root.startswith(pat.rstrip(os.sep) + os.sep):
                skip_dir = True
                break
        if skip_dir:
            dirs[:] = []
            continue
        # Prune subdirectories matching ignore patterns
        new_dirs = []
        for d in dirs:
            rel_d = os.path.join(rel_root, d) if rel_root != os.curdir else d
            if any(fnmatch(rel_d, pat) or rel_d.startswith(pat.rstrip(os.sep) + os.sep)
                   for pat in patterns):
                continue
            new_dirs.append(d)
        dirs[:] = new_dirs
        # Snapshot files without prior logs
        for fname in files:
            rel_path = os.path.join(rel_root, fname) if rel_root != os.curdir else fname
            if any(fnmatch(rel_path, pat) or rel_path.startswith(pat.rstrip(os.sep) + os.sep)
                   for pat in patterns):
                continue
            safe = urllib.parse.quote(rel_path, safe='')
            log_path = os.path.join(store.root, safe + '.jsonl')
            if not force and os.path.exists(log_path):
                continue
            abs_path = os.path.join(base_path, rel_path)
            content = None
            try:
                size = os.path.getsize(abs_path)
                if size <= 100 * 1024 * 1024:
                    with open(abs_path, 'rb') as f:
                        content = f.read()
                else:
                    logger.warning(f"Skipping large file on ingest: {rel_path} ({size} bytes)")
            except Exception:
                content = None
            store.record(rel_path, 'created', content)
            logger.info(f"Ingested: {rel_path}")


class MirrorEventHandler(FileSystemEventHandler):
    """
    File system events handler that records snapshots on each file change,
    with debounce and deduplication based on content hashes.
    """
    def __init__(self, store, base_path):
        super().__init__()
        self.store = store
        self.base_path = os.path.abspath(base_path)
        # Load ignore patterns from .bmlignore and defaults
        self.ignore_patterns = load_ignore_patterns(self.base_path)
        # Debounce interval (seconds) and state for deduplication; set to 0 to disable
        try:
            self._debounce_interval = float(os.environ.get('BML_DEBOUNCE_INTERVAL', 0.5))
        except Exception:
            self._debounce_interval = 0.5
        self._timers = {}       # rel_path -> threading.Timer
        self._last_hash = {}    # rel_path -> last SHA256 digest
        ignore_file = os.path.join(self.base_path, '.bmlignore')
        if os.path.isfile(ignore_file):
            try:
                with open(ignore_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        p = line.strip()
                        if p and not p.startswith('#'):
                            self.ignore_patterns.append(p)
            except Exception:
                pass

    def on_any_event(self, event):
        # Ignore directory events
        if event.is_directory:
            return

        # Handle file moves/renames as delete+create (immediate)
        if event.event_type == 'moved' and hasattr(event, 'dest_path'):
            try:
                old_rel = os.path.relpath(event.src_path, self.base_path)
                new_rel = os.path.relpath(event.dest_path, self.base_path)
            except ValueError:
                return
            # Ignore patterns for both old and new
            for pat in self.ignore_patterns:
                if fnmatch(old_rel, pat) or old_rel.startswith(pat.rstrip(os.sep) + os.sep):
                    return
                if fnmatch(new_rel, pat) or new_rel.startswith(pat.rstrip(os.sep) + os.sep):
                    return
            # Treat as deletion of old path
            self._cancel_pending(old_rel)
            self._last_hash.pop(old_rel, None)
            self.store.record(old_rel, 'deleted', None)
            logger.info(f"Deleted: {old_rel}")
            # Immediate creation of new path
            content = None
            try:
                size = os.path.getsize(event.dest_path)
                if size <= 100 * 1024 * 1024:
                    with open(event.dest_path, 'rb') as f:
                        content = f.read()
                else:
                    logger.warning(f"Ignoring large file on move: {new_rel} ({size} bytes)")
            except Exception:
                content = None
            self.store.record(new_rel, 'created', content)
            logger.info(f"Created: {new_rel}")
            return

        # Compute relative path and skip if ignored
        try:
            rel_path = os.path.relpath(event.src_path, self.base_path)
        except ValueError:
            return
        if any(fnmatch(rel_path, pat) or rel_path.startswith(pat.rstrip(os.sep) + os.sep)
               for pat in self.ignore_patterns):
            return

        # Handle deletions: cancel debounced, clear hash, record immediately
        if event.event_type == 'deleted':
            self._cancel_pending(rel_path)
            self._last_hash.pop(rel_path, None)
            self.store.record(rel_path, 'deleted', None)
            logger.info(f"Deleted: {rel_path}")
            return

        # Debounce create/modify events: schedule flush
        if event.event_type in ('created', 'modified'):
            # Debounce or immediate flush based on interval
            self._cancel_pending(rel_path)
            if self._debounce_interval <= 0:
                self._flush_event(rel_path)
            else:
                t = threading.Timer(self._debounce_interval, self._flush_event, args=(rel_path,))
                t.daemon = True
                self._timers[rel_path] = t
                t.start()
            return

    def _cancel_pending(self, rel_path):
        """Cancel any pending debounce timer for a path."""
        t = self._timers.pop(rel_path, None)
        if t:
            t.cancel()

    def _flush_event(self, rel_path):
        """Process a debounced create/modify: read, hash, and record if content changed."""
        # Remove timer entry
        self._timers.pop(rel_path, None)
        abs_path = os.path.join(self.base_path, rel_path)
        try:
            size = os.path.getsize(abs_path)
        except Exception:
            return
        if size > 100 * 1024 * 1024:
            logger.warning(f"Skipping large file: {rel_path} ({size} bytes)")
            return
        try:
            with open(abs_path, 'rb') as f:
                content = f.read()
        except Exception:
            return
        # Compute hash and dedupe
        digest = hashlib.sha256(content).hexdigest()
        prev = self._last_hash.get(rel_path)
        if prev == digest:
            return
        # Determine event type: first time -> created, else modified
        ev = 'created' if prev is None else 'modified'
        self._last_hash[rel_path] = digest
        self.store.record(rel_path, ev, content)
        logger.info(f"{ev.title()}: {rel_path}")




def start_watch(path):
    """
    Start monitoring the given directory path for changes.
    """
    base_path = os.path.abspath(path)
    if not os.path.isdir(base_path):
        logger.error(f"Not a directory: {base_path}")
        sys.exit(1)

    store = MirrorStore()
    # Bootstrap ignore patterns and ingest existing files before watching
    auto_bootstrap_ignore(base_path)
    ingest_tree(base_path, store)
    handler = MirrorEventHandler(store, base_path)
    observer = Observer()
    observer.schedule(handler, base_path, recursive=True)
    observer.start()
    logger.info(f"Watching {base_path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()