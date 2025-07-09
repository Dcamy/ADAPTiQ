import os
import json
import time
import base64
import platform


class MirrorStore:
    """
    Handles writing file-change snapshots to a per-file JSONL log store.
    """
    def __init__(self):
        self.root = self._default_store_dir()
        os.makedirs(self.root, exist_ok=True)

    @staticmethod
    def _default_store_dir():
        # Use OS-specific path outside project folders
        if platform.system() == "Windows":
            local = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
            return os.path.join(local, "blackmirror_lite", "mirrors")
        # Linux/macOS default under home directory
        return os.path.join(os.path.expanduser("~"), ".blackmirror_lite", "mirrors")

    def record(self, relative_path, event_type, content_bytes):
        """
        Append a JSON line for this change event. Content is base64-encoded if provided.
        """
        # Normalize filename for the log file
        safe_name = relative_path.replace(os.sep, "__")
        log_path = os.path.join(self.root, safe_name + ".jsonl")
        entry = {
            "timestamp": time.time(),
            "event": event_type,
        }
        if content_bytes is not None:
            entry["content_b64"] = base64.b64encode(content_bytes).decode("ascii")
        with open(log_path, "a", encoding="utf-8") as logf:
            logf.write(json.dumps(entry) + "\n")