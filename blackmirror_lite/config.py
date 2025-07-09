"""
Configuration management for BlackMirror Lite tracked folders.
"""
import os
import json


def _config_dir():
    """Return the base directory for BlackMirror Lite data (parent of mirrors)."""
    # MirrorStore stores under ~/.blackmirror_lite/mirrors or %LOCALAPPDATA%/.../mirrors
    # Config file should live alongside the mirrors directory.
    try:
        from .store import MirrorStore
        store_root = MirrorStore._default_store_dir()
    except ImportError:
        # Fallback to home directory
        store_root = os.path.join(os.path.expanduser("~"), ".blackmirror_lite", "mirrors")
    return os.path.dirname(store_root)


def _config_path():
    """Return the full path to the tracked-folders config file."""
    return os.path.join(_config_dir(), "config.json")


def load_tracked():
    """Load the list of tracked folder paths from config. Returns a list."""
    cfg_file = _config_path()
    if not os.path.exists(cfg_file):
        return []
    try:
        with open(cfg_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('paths', [])
    except Exception:
        return []


def save_tracked(paths):
    """Save the list of tracked folder paths to config (overwrites)."""
    cfg_dir = _config_dir()
    os.makedirs(cfg_dir, exist_ok=True)
    cfg_file = _config_path()
    tmp_file = cfg_file + '.tmp'
    data = {'paths': paths}
    with open(tmp_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        f.write('\n')
    os.replace(tmp_file, cfg_file)


def add_tracked(path):
    """Add a folder path to tracked config (idempotent)."""
    abs_path = os.path.abspath(path)
    paths = load_tracked()
    if abs_path not in paths:
        paths.append(abs_path)
        save_tracked(paths)
    return abs_path


def remove_tracked(path):
    """Remove a folder path from tracked config. Returns True if removed."""
    abs_path = os.path.abspath(path)
    paths = load_tracked()
    if abs_path in paths:
        paths = [p for p in paths if p != abs_path]
        save_tracked(paths)
        return True
    return False