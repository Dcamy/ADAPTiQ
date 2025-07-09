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
        help="Relative paths to leave untouched",
    )
    sub.add_parser("watch", help="Run watcher manually (not implemented)")
    sub.add_parser("install-autostart", help="Install autostart (not implemented)")

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

    elif args.command in ("watch", "install-autostart"):
        parser.error(f"Command '{args.command}' is not yet implemented.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()