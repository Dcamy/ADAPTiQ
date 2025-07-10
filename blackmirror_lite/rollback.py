"""
Rollback engine for BlackMirror Lite: restore tracked folders to a given time delta.
"""
import os
import sys
import time
import json
import base64
import re
from fnmatch import fnmatch

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
    # Always preserve .git and .env by default
    default_keeps = ['.git', '.env']
    if keep_paths is None:
        keep_paths = default_keeps.copy()
    else:
        # merge user-specified with defaults
        keep_paths = default_keeps + list(keep_paths)

    tracked = load_tracked()
    if not tracked:
        print("Error: no tracked folders configured.")
        sys.exit(1)

    # Determine which tracked root(s) to apply rollback to
    if target:
        abs_target = os.path.abspath(target)
        bases = [b for b in tracked if abs_target == b or abs_target.startswith(b + os.sep)]
        if not bases:
            print(f"Error: target '{target}' is not under any tracked folder.")
            sys.exit(1)
        rel_prefix = os.path.relpath(abs_target, bases[0])
    else:
        cwd = os.getcwd()
        bases = [b for b in tracked if cwd == b or cwd.startswith(b + os.sep)]
        if not bases:
            print("Error: current directory not under any tracked folder. Please specify a path.")
            sys.exit(1)
        rel_prefix = None

    # Normalize only patterns
    only_patterns = only or []

    cutoff = time.time() - delta_seconds
    store_dir = MirrorStore._default_store_dir()

    for fname in os.listdir(store_dir):
        if not fname.endswith('.jsonl'):
            continue
        safe_name = fname[:-6]
        rel_path = safe_name.replace('__', os.sep)

        # Scope to rel_prefix if given
        if rel_prefix:
            if rel_path != rel_prefix and not rel_path.startswith(rel_prefix + os.sep):
                continue
            rel_path = rel_path[len(rel_prefix) + 1:]

        # Apply --only filters if present
        if only_patterns:
            if not any(fnmatch(rel_path, pat) for pat in only_patterns):
                continue

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