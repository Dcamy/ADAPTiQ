import os
from pathlib import Path

import pytest
from watchdog.events import FileSystemEvent

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