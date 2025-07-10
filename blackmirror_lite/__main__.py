import argparse
import os

"""Command-line interface for BlackMirror Lite."""


def main():
    parser = argparse.ArgumentParser(
        prog="blackmirror_lite",
        description="BlackMirror Lite: filesystem-based snapshot time machine",
    )
    sub = parser.add_subparsers(dest="command")

    track = sub.add_parser("track", help="Start tracking a folder")
    track.add_argument("path", help="Path to folder to track")

    untrack = sub.add_parser("untrack", help="Stop tracking a folder")
    untrack.add_argument("path", help="Path to folder to untrack")

    sub.add_parser("list", help="List tracked folders")
    jb = sub.add_parser(
        "jump-back",
        help="Rollback to a time delta (e.g. '2h', '30m')",
    )
    jb.add_argument("delta", help="Time delta to jump back (e.g. 2h, 30m)")
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

    args = parser.parse_args()
    if args.command == "track":
        from .config import add_tracked
        # import watcher only when needed; avoids requiring watchdog for list/untrack
        from .watcher import start_watch

        folder = add_tracked(args.path)
        print(f"Tracking: {folder}")
        start_watch(folder)

    elif args.command == "untrack":
        from .config import remove_tracked

        removed = remove_tracked(args.path)
        if removed:
            print(f"Untracked: {os.path.abspath(args.path)}")
        else:
            print(f"Not tracked: {args.path}")

    elif args.command == "list":
        from .config import load_tracked

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
        jump_back(secs, args.keep)

    elif args.command == "watch":
        import sys, time
        from .config import load_tracked
        from .store import MirrorStore
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

    else:
        parser.error(f"Command '{args.command}' is not yet implemented.")


if __name__ == "__main__":
    main()