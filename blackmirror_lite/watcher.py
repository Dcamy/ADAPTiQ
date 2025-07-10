import os
import sys
import time
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .store import MirrorStore
from fnmatch import fnmatch

# configure simple console logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class MirrorEventHandler(FileSystemEventHandler):
    """
    File system events handler that records snapshots on each file change.
    """
    def __init__(self, store, base_path):
        super().__init__()
        self.store = store
        self.base_path = os.path.abspath(base_path)
        # Load ignore patterns from .bmlignore and defaults
        self.ignore_patterns = ['.git', '.env', '.bmlignore']
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
        # Ignore directory events and apply ignore patterns
        if event.is_directory:
            return
        try:
            rel_path = os.path.relpath(event.src_path, self.base_path)
        except ValueError:
            return
        for pat in self.ignore_patterns:
            if fnmatch(rel_path, pat) or rel_path.startswith(pat.rstrip(os.sep) + os.sep):
                return

        # Read file content on create/modify, skipping large files
        content = None
        if event.event_type in ("created", "modified"):
            try:
                size = os.path.getsize(event.src_path)
                # Skip files larger than threshold (100MB)
                if size > 100 * 1024 * 1024:
                    logger.warning(f"Ignoring large file: {rel_path} ({size} bytes)")
                    return
                with open(event.src_path, "rb") as f:
                    content = f.read()
            except Exception:
                content = None

        # Record the snapshot
        self.store.record(rel_path, event.event_type, content)
        logger.info(f"{event.event_type.title()}: {rel_path}")


def start_watch(path):
    """
    Start monitoring the given directory path for changes.
    """
    base_path = os.path.abspath(path)
    if not os.path.isdir(base_path):
        logger.error(f"Not a directory: {base_path}")
        sys.exit(1)

    store = MirrorStore()
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