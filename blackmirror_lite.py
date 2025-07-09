# path: blackmirror_lite/blackmirror_lite.py

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

OUTPUT_ROOT = Path(os.getenv('BLACKMIRROR_OUTPUT', os.path.expanduser(
    "~/.blackmirror_lite"))).resolve()

def safe_path(path):
    return str(path).replace(":", "").replace("\\", "/")

class MirrorHandler(FileSystemEventHandler):
    def __init__(self, root_path):
        self.root_path = Path(root_path).resolve()

    def on_modified(self, event):
        if event.is_directory or not os.path.isfile(event.src_path):
            return
        try:
            rel_path = Path(event.src_path).resolve().relative_to(self.root_path)
            mirror_path = OUTPUT_ROOT / safe_path(self.root_path) / rel_path
            mirror_path.parent.mkdir(parents=True, exist_ok=True)
            with open(event.src_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            record = {
                "ts": datetime.utcnow().isoformat() + "Z",
                "content": content
            }
            with open(mirror_path.with_suffix(".jsonl"), "a", encoding="utf-8") as out:
                out.write(json.dumps(record) + "\n")
            print(f"[🔁] Saved: {rel_path}")
        except Exception as e:
            print(f"[⚠️] Error processing {event.src_path}: {e}")

def start_watch(path):
    path = Path(path).resolve()
    print(f"[👁] Watching {path}...")
    event_handler = MirrorHandler(path)
    observer = Observer()
    observer.schedule(event_handler, str(path), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python blackmirror_lite.py <path/to/project>")
        sys.exit(1)
    start_watch(sys.argv[1])
