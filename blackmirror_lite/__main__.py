import argparse
import os
import sys
import time
import shutil
import json
import base64
import urllib.request
from .store import MirrorStore, parse_size
import urllib.parse
from .config import load_tracked, add_tracked, remove_tracked, _config_dir
from .rollback import jump_back
from . import __version__
try:
    from plyer import notification
except ImportError:
    notification = None

def _warn_store_size():
    """Warn if the mirror store size exceeds the configured threshold."""
    # Default threshold, override via BML_STORE_WARNING_THRESHOLD (e.g. '5G', '500M')
    threshold_str = os.environ.get('BML_STORE_WARNING_THRESHOLD', '10G')
    try:
        threshold = parse_size(threshold_str)
    except ValueError:
        threshold = 10 * 1024**3
        threshold_str = '10G'
    store_dir = MirrorStore._default_store_dir()
    total = 0
    for root, dirs, files in os.walk(store_dir):
        for fname in files:
            try:
                total += os.path.getsize(os.path.join(root, fname))
            except Exception:
                pass
    if total > threshold:
        print(
            f"⚠️ Mirror store >{threshold_str}. "
            f"Consider running `bml prune --max-size {threshold_str}` or tighten your `.bmlignore`."
        )

def check_update():
    """Check PyPI for a newer release and notify via console and desktop."""
    local_ver = __version__
    remote_ver = None
    # Query PyPI JSON API for latest version
    try:
        with urllib.request.urlopen(
            "https://pypi.org/pypi/blackmirror_lite/json"
        ) as resp:
            data = json.load(resp)
            remote_ver = data.get('info', {}).get('version')
    except Exception as e:
        print(f"Could not fetch version info from PyPI: {e}")
    if remote_ver:
        if remote_ver != local_ver:
            msg = f"Update available: {local_ver} → {remote_ver}"
            print(msg)
            # Determine updater command (pip or pipx)
            if 'site-packages' in __file__:
                cmd = 'pip install --upgrade blackmirror_lite'
            else:
                cmd = 'pipx upgrade blackmirror-lite'
            print(f"To update, run: {cmd}")
            if notification:
                notification.notify(title="BlackMirror Lite Update", message=msg)
        else:
            print(f"BlackMirror Lite is up to date (version {local_ver})")
    else:
        print("Unable to determine remote version.")

"""Command-line interface for BlackMirror Lite."""


def _human_size(num):
    for unit in ('B','KB','MB','GB','TB'):
        if num < 1024.0 or unit == 'TB':
            return f"{num:.1f} {unit}"
        num /= 1024.0

def _event_icon(evt):
    if evt in ('created','modified'):
        return '💾'
    if evt == 'deleted':
        return '❌'
    return '🔄'

def run_prove_it_demo():
    config_dir = _config_dir()
    demo_dir = os.path.join(config_dir, 'demo')
    shutil.rmtree(demo_dir, ignore_errors=True)
    os.makedirs(demo_dir)
    demo_file = os.path.join(demo_dir, 'demo.py')
    store = MirrorStore()
    add_tracked(demo_dir)
    def write_and_record(content):
        with open(demo_file, 'w', encoding='utf-8') as f:
            f.write(content)
        store.record('demo.py', 'modified', content.encode())
    print('Running initial snapshot test to prove BlackMirror works...')
    write_and_record('print(1)\n')
    time.sleep(3)
    write_and_record('print(2)\n')
    time.sleep(3)
    write_and_record('print(3)\n')
    # Roll back the demo directory by 3 seconds to test snapshot/rollback
    jump_back(3, target=demo_dir)
    remove_tracked(demo_dir)
    try:
        with open(demo_file, 'r', encoding='utf-8') as f:
            result = f.read().strip()
    except Exception:
        result = ''
    if result == 'print(2)':
        print('✅ BlackMirror works')
        return True
    print('❌ Well shit. You found an edge case. Open an issue and brag about it:')
    print('https://github.com/Dcamy/ADAPTiQ/issues')
    return False

def main():
    parser = argparse.ArgumentParser(
        prog="blackmirror_lite",
        description="BlackMirror Lite: filesystem-based snapshot time machine",
    )
    sub = parser.add_subparsers(dest="command")

    track = sub.add_parser("track", help="Start tracking a folder")
    track.add_argument("path", help="Path to folder to track (or 'me' for current directory)")

    untrack = sub.add_parser("untrack", help="Stop tracking a folder")
    untrack.add_argument("path", help="Path to folder to untrack")

    sub.add_parser("list", help="List tracked folders")
    jb = sub.add_parser(
        "jump-back",
        help="Rollback to a time delta (e.g. '2h', '30m')",
    )
    jb.add_argument("delta", help="Time delta to jump back (e.g. 2h, 30m)")
    jb.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Optional path (folder or file) to rollback (defaults to current directory)",
    )
    jb.add_argument(
        "--only",
        nargs="+",
        default=None,
        help="Only rollback these relative file paths or glob patterns under the target",
    )
    jb.add_argument(
        "--keep",
        nargs="+",
        default=[],
        help="Relative paths to leave untouched ('.git' and '.env' are always preserved)",
    )
    sub.add_parser("watch", help="Run watcher manually for all tracked folders")
    sub.add_parser(
        "install-autostart",
        help="Install autostart task so watcher runs on login/boot",
    )
    sub.add_parser("status", help="Show tracking status, mirror paths, recent actions")
    sub.add_parser("prove-it", help="Run a self-contained demo proving snapshot/rollback works")
    sub.add_parser("update", help="Check for new versions and notify via desktop notification")
    pr = sub.add_parser("prune", help="Prune old snapshots by age or size")
    pr.add_argument("--keep-days", type=int, default=None, help="Retain only entries newer than DAYS days")
    pr.add_argument("--max-size", default=None, help="Prune oldest logs until total size <= SIZE (e.g. 100M, 2G)")

    args = parser.parse_args()
    mirror_dir = MirrorStore._default_store_dir()
    _warn_store_size()
    # On first use, auto-run the demo once (but skip it for 'prove-it' or 'update')
    if args.command not in ('prove-it', 'update') and (not os.path.isdir(mirror_dir) or not os.listdir(mirror_dir)):
        success = run_prove_it_demo()
        if not success:
            sys.exit(1)
    if args.command == "track":
        from .watcher import start_watch

        # Interpret 'me' as current working directory
        target = args.path
        if target == 'me':
            target = os.getcwd()
        folder = os.path.abspath(target)
        # Guard against nested tracking
        existing = load_tracked()
        for root in existing:
            if folder.startswith(root + os.sep):
                print(f"Error: '{folder}' is already under tracked folder '{root}'")
                sys.exit(1)
            if root.startswith(folder + os.sep):
                print(f"Error: tracked folder '{root}' is nested under '{folder}'")
                sys.exit(1)

        folder = add_tracked(folder)
        print(f"Tracking: {folder}")
        start_watch(folder)

    elif args.command == "untrack":
        removed = remove_tracked(args.path)
        if removed:
            print(f"Untracked: {os.path.abspath(args.path)}")
        else:
            print(f"Not tracked: {args.path}")

    elif args.command == "list":
        paths = load_tracked()
        if not paths:
            print("No tracked folders.")
        else:
            for p in paths:
                print(p)

    elif args.command == "jump-back":
        from .rollback import parse_timedelta, jump_back

        try:
            secs = parse_timedelta(args.delta)
        except ValueError as e:
            parser.error(str(e))
        try:
            jump_back(secs, args.keep, target=args.path, only=args.only)
        except Exception as e:
            parser.error(str(e))

    elif args.command == "watch":
        from .watcher import MirrorEventHandler
        from watchdog.observers import Observer

        bases = load_tracked()
        if not bases:
            print("No tracked folders configured. Use 'track' first.")
            sys.exit(1)

        store = MirrorStore()
        observer = Observer()
        for base in bases:
            handler = MirrorEventHandler(store, base)
            observer.schedule(handler, base, recursive=True)
            print(f"Watching: {base}")
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    elif args.command == "install-autostart":
        from .autostart import install_autostart

        install_autostart()
    elif args.command == "update":
        check_update()

    elif args.command == "status":
        store = MirrorStore()
        roots = load_tracked()
        if not roots:
            print("No tracked folders.")
            sys.exit(1)
        for base in roots:
            print(f"Tracking: {base}")
            print(f"Backups: {store.root}")
            events = []
            for fname in os.listdir(store.root):
                if not fname.endswith('.jsonl'):
                    continue
                safe = fname[:-6]
                rel = urllib.parse.unquote(safe)
                log_path = os.path.join(store.root, fname)
                try:
                    last = None
                    with open(log_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            entry = json.loads(line)
                            last = entry
                    if last:
                        events.append((last.get('timestamp', 0), last.get('event', ''), rel, last.get('content_b64')))
                except Exception:
                    continue
            events.sort(key=lambda e: e[0], reverse=True)
            print("Last 3 actions:")
            for ts, evt, rel, b64 in events[:3]:
                t_str = time.strftime("%H:%M:%S", time.localtime(ts))
                size_str = ""
                if b64:
                    data = base64.b64decode(b64.encode('ascii'))
                    size_str = f" ({_human_size(len(data))})"
                print(f"[{_event_icon(evt)}] {t_str} | {evt} | {rel}{size_str}")

    elif args.command == "prove-it":
        success = run_prove_it_demo()
        if not success:
            sys.exit(1)

    elif args.command == "prune":
        try:
            store = MirrorStore()
            store.prune(keep_days=args.keep_days, max_size=args.max_size)
        except ValueError as e:
            parser.error(str(e))
        print("Prune complete.")
    else:
        parser.error(f"Command '{args.command}' is not yet implemented.")


if __name__ == "__main__":
    main()