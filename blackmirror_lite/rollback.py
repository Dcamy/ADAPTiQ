"""
Rollback engine for BlackMirror Lite: restore tracked folders to a given time delta.
"""
import os
import sys
import time
import json
import base64
import re

from .store import MirrorStore
from .config import load_tracked


def parse_timedelta(delta_str):
    """
    Parse a human-friendly time delta like '2h', '30m', '15s', '1d' into seconds.
    Raises ValueError on invalid format.
    """
    m = re.match(r'^(\d+)([smhd])$', delta_str)
    if not m:
        raise ValueError(f"Invalid time delta: {delta_str}")
    val, unit = m.groups()
    val = int(val)
    if unit == 's':
        return val
    if unit == 'm':
        return val * 60
    if unit == 'h':
        return val * 3600
    if unit == 'd':
        return val * 86400
    # should not reach here
    raise ValueError(f"Unknown time unit: {unit}")


def jump_back(delta_seconds, keep_paths=None):
    """
    Restore all tracked folders to how they looked delta_seconds ago.

    keep_paths: iterable of relative path prefixes to leave untouched.
    """
    if keep_paths is None:
        keep_paths = []

    bases = load_tracked()
    if not bases:
        print("Error: no tracked folders configured.")
        sys.exit(1)

    cutoff = time.time() - delta_seconds
    store_dir = MirrorStore._default_store_dir()

    for fname in os.listdir(store_dir):
        if not fname.endswith('.jsonl'):
            continue
        safe_name = fname[:-6]
        rel_path = safe_name.replace('__', os.sep)
        # Skip paths user wants to keep
        if any(rel_path == kp or rel_path.startswith(kp.rstrip(os.sep) + os.sep)
               for kp in keep_paths):
            continue

        log_path = os.path.join(store_dir, fname)
        last_entry = None
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = json.loads(line)
                    if entry.get('timestamp', 0) <= cutoff:
                        last_entry = entry
        except Exception:
            continue

        # Apply rollback
        for base in bases:
            target = os.path.join(base, rel_path)

            # No snapshot before cutoff -> delete file if exists
            if last_entry is None or last_entry.get('event') == 'deleted':
                if os.path.exists(target):
                    os.remove(target)
                continue

            # Restore content snapshot
            b64 = last_entry.get('content_b64')
            if b64 is None:
                # No content recorded -> skip
                continue
            data = base64.b64decode(b64)
            # ensure directory exists
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, 'wb') as f:
                f.write(data)

    print(f"Rollback to {delta_seconds}s ago complete.")