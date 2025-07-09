import os
import sys
import time
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .store import MirrorStore

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

    def on_any_event(self, event):
        # Ignore directory events
        if event.is_directory:
            return
        # Determine relative path
        try:
            rel_path = os.path.relpath(event.src_path, self.base_path)
        except ValueError:
            # src_path not under base_path
            return

        # Read file content on create/modify
        content = None
        if event.event_type in ("created", "modified"):
            try:
                with open(event.src_path, "rb") as f:
                    content = f.read()
            except Exception:
                # File may have been removed or unreadable
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