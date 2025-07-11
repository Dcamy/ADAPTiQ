import os
import json
import time
import base64
import platform
import urllib.parse

_WSL_PROC_PATH = "/proc/version"

def _is_wsl():
    """Detect Windows Subsystem for Linux by inspecting /proc/version."""
    if platform.system() != "Linux":
        return False
    try:
        with open(_WSL_PROC_PATH, 'r') as f:
            return 'Microsoft' in f.read() or 'microsoft' in f.read()
    except Exception:
        return False


class MirrorStore:
    """
    Handles writing file-change snapshots to a per-file JSONL log store.

    If initialized with a root_key (e.g. a tracked folder path), snapshots
    go into a subdirectory under the global mirror store, isolating each
    tracked root.
    """
    def __init__(self, root_key=None):
        self.root = self._default_store_dir()
        if root_key:
            # Create a per-root subdirectory to avoid cross-root collisions
            safe = urllib.parse.quote(root_key, safe='')
            self.root = os.path.join(self.root, safe)
        os.makedirs(self.root, exist_ok=True)

    @staticmethod
    def _default_store_dir():
        # Use Windows local-appdata path on Windows or under WSL;
        # otherwise default to a hidden folder under the home directory (Linux/macOS).
        system = platform.system()
        if system == "Windows" or (system == "Linux" and _is_wsl()):
            local = os.environ.get("LOCALAPPDATA")
            if not local:
                # Fallback for WSL if LOCALAPPDATA not inherited
                try:
                    import getpass

                    user = os.environ.get("USERNAME") or getpass.getuser()
                    local = os.path.join("/mnt/c", "Users", user, "AppData", "Local")
                except Exception:
                    local = os.path.expanduser("~")
            return os.path.join(local, "blackmirror_lite", "mirrors")
        # Linux/macOS default under home directory
        return os.path.join(os.path.expanduser("~"), ".blackmirror_lite", "mirrors")

    def record(self, relative_path, event_type, content_bytes):
        """
        Append a JSON line for this change event. Content is base64-encoded if provided.
        Uses URL-safe encoding of the relative path to avoid collisions.
        """
        # Encode the path into a filesystem-safe, reversible string
        safe_name = urllib.parse.quote(relative_path, safe='')
        log_path = os.path.join(self.root, safe_name + ".jsonl")
        entry = {
            "timestamp": time.time(),
            "event": event_type,
        }
        if content_bytes is not None:
            entry["content_b64"] = base64.b64encode(content_bytes).decode("ascii")
        with open(log_path, "a", encoding="utf-8") as logf:
            logf.write(json.dumps(entry) + "\n")

    def prune(self, keep_days=None, max_size=None):
        """
        Prune snapshot logs by age (keep_days) and/or total size (max_size).

        keep_days: retain entries newer than this many days.
        max_size: prune oldest files until total store size <= max_size (bytes or human suffix).
        """
        # Age-based pruning
        if keep_days is not None:
            cutoff = time.time() - (keep_days * 86400)
            for fname in os.listdir(self.root):
                if not fname.endswith('.jsonl'):
                    continue
                path = os.path.join(self.root, fname)
                kept = []
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        for line in f:
                            entry = json.loads(line)
                            if entry.get('timestamp', 0) >= cutoff:
                                kept.append(entry)
                except Exception:
                    continue
                if kept:
                    tmp = path + '.tmp'
                    with open(tmp, 'w', encoding='utf-8') as tf:
                        for entry in kept:
                            tf.write(json.dumps(entry) + "\n")
                    os.replace(tmp, path)
                else:
                    try:
                        os.remove(path)
                    except Exception:
                        pass

        # Size-based pruning
        if max_size is not None:
            # Allow human-friendly sizes
            if isinstance(max_size, str):
                max_size = parse_size(max_size)
            files = []
            total = 0
            for fname in os.listdir(self.root):
                if not fname.endswith('.jsonl'):
                    continue
                path = os.path.join(self.root, fname)
                try:
                    st = os.stat(path)
                except Exception:
                    continue
                files.append((st.st_mtime, path, st.st_size))
                total += st.st_size
            files.sort(key=lambda x: x[0])
            for _, path, size in files:
                if total <= max_size:
                    break
                try:
                    os.remove(path)
                    total -= size
                except Exception:
                    pass

def parse_size(size_str):
    """
    Parse a human-friendly size string (e.g. '100M', '2G') into bytes.
    """
    m = __import__('re').match(r'^(\d+)([KMGTP])?$', size_str.strip(), __import__('re').IGNORECASE)
    if not m:
        raise ValueError(f"Invalid size: {size_str}")
    val = int(m.group(1))
    unit = (m.group(2) or '').upper()
    if unit == 'K':
        return val * 1024
    if unit == 'M':
        return val * 1024**2
    if unit == 'G':
        return val * 1024**3
    if unit == 'T':
        return val * 1024**4
    if unit == 'P':
        return val * 1024**5
    return val