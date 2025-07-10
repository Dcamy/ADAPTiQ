import os
import json
import base64

from blackmirror_lite.store import MirrorStore


def test_record_appends_jsonl(tmp_path, monkeypatch):
    # Redirect store root to temporary directory
    monkeypatch.setattr(MirrorStore, "_default_store_dir", staticmethod(lambda: str(tmp_path)))
    store = MirrorStore()

    rel = os.path.join("sub", "test.txt")
    content = b"hello world"
    store.record(rel, "modified", content)

    # JSONL file should be created with safe name
    import urllib.parse
    safe_name = urllib.parse.quote(rel, safe='')
    log_file = tmp_path / f"{safe_name}.jsonl"
    assert log_file.exists()

    # Validate content of the JSONL entry
    with open(log_file, "r", encoding="utf-8") as f:
        entry = json.loads(f.readline())
    assert entry["event"] == "modified"
    assert base64.b64decode(entry["content_b64"].encode("ascii")) == content
    assert "timestamp" in entry