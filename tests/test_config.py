import os

import pytest

from blackmirror_lite.config import load_tracked, add_tracked, remove_tracked
from blackmirror_lite.store import MirrorStore


def test_add_and_remove_tracked(tmp_path, monkeypatch):
    # Redirect store root to temporary directory for config storage
    fake_store_root = tmp_path / "mirrors"
    monkeypatch.setattr(MirrorStore, "_default_store_dir", staticmethod(lambda: str(fake_store_root)))

    # Initially no tracked folders
    assert load_tracked() == []

    # Add a folder path
    path = "/some/folder"
    abs_path = os.path.abspath(path)
    result = add_tracked(path)
    assert result == abs_path
    assert load_tracked() == [abs_path]

    # Removing a non-tracked path returns False
    assert not remove_tracked("/other")

    # Remove the tracked path
    assert remove_tracked(path)
    assert load_tracked() == []