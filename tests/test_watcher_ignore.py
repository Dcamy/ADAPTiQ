import os
from pathlib import Path

import pytest
from watchdog.events import FileSystemEvent

from watchdog.events import FileMovedEvent

from blackmirror_lite.watcher import MirrorEventHandler


class DummyStore:
    def __init__(self):
        self.recorded = []

    def record(self, rel_path, event_type, content_bytes):
        self.recorded.append((rel_path, event_type, content_bytes))


def make_event(src_path, event_type):
    ev = FileSystemEvent(src_path)
    ev.event_type = event_type
    ev.src_path = src_path
    ev.is_directory = False
    return ev


def test_bmlignore_pattern_skips_file(tmp_path):
    # Create a dummy project with .bmlignore ignoring foo.txt
    base = tmp_path / "proj"
    base.mkdir()
    ignore_file = base / ".bmlignore"
    ignore_file.write_text("foo.txt\n")

    # Dummy store to capture record calls
    store = DummyStore()
    handler = MirrorEventHandler(store, str(base))

    # foo.txt should be ignored
    foo = base / "foo.txt"
    foo.write_text("hello")
    ev1 = make_event(str(foo), "modified")
    handler.on_any_event(ev1)
    assert store.recorded == []

    # bar.txt should be recorded
    bar = base / "bar.txt"
    bar.write_text("world")
    ev2 = make_event(str(bar), "modified")
    handler.on_any_event(ev2)
    assert store.recorded and store.recorded[0][0] == "bar.txt"


def test_move_event_records_delete_and_create(tmp_path):
    base = tmp_path / "proj"
    base.mkdir()
    # Create a source file to move
    src = base / "old.txt"
    src.write_text("hello")

    store = DummyStore()
    handler = MirrorEventHandler(store, str(base))

    # Simulate moving old.txt → new.txt
    dest = base / "new.txt"
    # Actually move the file on disk to simulate a real rename
    src.rename(dest)
    ev = FileMovedEvent(str(src), str(dest))
    handler.on_any_event(ev)

    # Expect delete of old and create of new with same content
    assert len(store.recorded) == 2
    assert store.recorded[0][0] == "old.txt" and store.recorded[0][1] == "deleted"
    assert store.recorded[1][0] == "new.txt" and store.recorded[1][1] == "created"
    assert store.recorded[1][2] == b"hello"