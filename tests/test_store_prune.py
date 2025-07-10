import os
import json
import time
import base64

import pytest

from blackmirror_lite.store import MirrorStore, parse_size


@pytest.mark.parametrize("s,expected", [
    ("5", 5),
    ("10K", 10 * 1024),
    ("2M", 2 * 1024**2),
    ("3G", 3 * 1024**3),
    ("1T", 1 * 1024**4),
])
def test_parse_size_valid(s, expected):
    assert parse_size(s) == expected


@pytest.mark.parametrize("s", ["", "5X", "K5", "12MB"])
def test_parse_size_invalid(s):
    with pytest.raises(ValueError):
        parse_size(s)


def test_prune_age(tmp_path, monkeypatch):
    # Setup mirror store in temp directory
    monkeypatch.setattr(MirrorStore, '_default_store_dir', staticmethod(lambda: str(tmp_path)))
    store = MirrorStore()

    # Create old snapshot (2 days ago) and new snapshot (now)
    old_file = tmp_path / 'old.jsonl'
    ts_old = time.time() - 2 * 86400
    entry_old = {'timestamp': ts_old, 'event': 'modified',
                 'content_b64': base64.b64encode(b'a').decode()}
    old_file.write_text(json.dumps(entry_old) + '\n', encoding='utf-8')

    new_file = tmp_path / 'new.jsonl'
    ts_new = time.time()
    entry_new = {'timestamp': ts_new, 'event': 'modified',
                 'content_b64': base64.b64encode(b'b').decode()}
    new_file.write_text(json.dumps(entry_new) + '\n', encoding='utf-8')

    # Prune entries older than 1 day
    store.prune(keep_days=1)
    assert not old_file.exists()
    assert new_file.exists()


def test_prune_size(tmp_path, monkeypatch):
    # Setup mirror store in temp directory
    monkeypatch.setattr(MirrorStore, '_default_store_dir', staticmethod(lambda: str(tmp_path)))
    store = MirrorStore()

    # Create three small logs to build total size
    for i in range(3):
        path = tmp_path / f'f{i}.jsonl'
        entry = {'timestamp': time.time(), 'event': 'modified',
                 'content_b64': base64.b64encode(b'x' * 512).decode()}
        line = json.dumps(entry) + '\n'
        # Repeat to increase file size
        path.write_text(line * 4, encoding='utf-8')

    # Prune to max size of 1 KB
    store.prune(max_size='1K')
    total = sum(p.stat().st_size for p in tmp_path.iterdir() if p.is_file())
    assert total <= 1024