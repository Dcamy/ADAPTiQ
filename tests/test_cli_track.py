import os
import sys
import json

import pytest

import blackmirror_lite.__main__ as cli
from blackmirror_lite.config import load_tracked
from blackmirror_lite.store import MirrorStore


@pytest.fixture(autouse=True)
def isolate_store(tmp_path, monkeypatch):
    """
    Redirect mirror store and config to a temporary directory for each test.
    """
    # Point store root to tmp_path/mirrors
    fake_store = tmp_path / "mirrors"
    monkeypatch.setattr(MirrorStore, '_default_store_dir', staticmethod(lambda: str(fake_store)))
    # Stub out the initial self-proof demo so CLI track tests don't trigger it
    monkeypatch.setattr(cli, 'run_prove_it_demo', lambda: True)
    # Ensure clean state and cleanup config after test
    yield
    cfg = tmp_path / 'config.json'
    if cfg.exists():
        cfg.unlink()


def test_track_me_adds_cwd(monkeypatch, tmp_path, capsys):
    # Simulate current working directory
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)

    # Prevent the watcher from blocking
    import blackmirror_lite.watcher as watcher
    monkeypatch.setattr(watcher, 'start_watch', lambda path: None)

    # Run CLI: track me
    monkeypatch.setattr(sys, 'argv', ['bml', 'track', 'me'])
    cli.main()

    # Should print tracking message
    captured = capsys.readouterr()
    assert f"Tracking: {project}" in captured.out

    # Config should include the project path
    tracked = load_tracked()
    assert tracked == [str(project)]


def test_nested_guardrail_parent(monkeypatch, tmp_path, capsys):
    # Setup: track a subdirectory first
    base = tmp_path / "base"
    sub = base / "subdir"
    sub.mkdir(parents=True)
    # Redirect store/config
    import blackmirror_lite.watcher as watcher
    monkeypatch.setattr(watcher, 'start_watch', lambda path: None)
    monkeypatch.setattr(sys, 'argv', ['bml', 'track', str(sub)])
    cli.main()
    capsys.readouterr()

    # Now attempt to track parent via 'me'
    monkeypatch.chdir(base)
    monkeypatch.setenv('BML_TEST', '1')  # no-op env var
    monkeypatch.setattr(sys, 'argv', ['bml', 'track', 'me'])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    out = capsys.readouterr().out
    assert "nested under" in out and str(sub) in out
    assert exc.value.code == 1


def test_nested_guardrail_child(monkeypatch, tmp_path, capsys):
    # Setup: track a parent first
    base = tmp_path / "base"
    sub = base / "subdir"
    sub.mkdir(parents=True)
    # Redirect store/config
    import blackmirror_lite.watcher as watcher
    monkeypatch.setattr(watcher, 'start_watch', lambda path: None)
    # Track base
    monkeypatch.setattr(sys, 'argv', ['bml', 'track', str(base)])
    cli.main()
    capsys.readouterr()

    # Now attempt track nested subdir via 'me'
    monkeypatch.chdir(sub)
    monkeypatch.setattr(sys, 'argv', ['bml', 'track', 'me'])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    out = capsys.readouterr().out
    assert "already under tracked folder" in out and str(base) in out
    assert exc.value.code == 1


def test_nested_guardrail_parent_direct(monkeypatch, tmp_path, capsys):
    # Track a subfolder first, then error when tracking its parent directly
    base = tmp_path / "base"
    sub = base / "subdir"
    sub.mkdir(parents=True)
    import blackmirror_lite.watcher as watcher
    monkeypatch.setattr(watcher, 'start_watch', lambda path: None)
    monkeypatch.setattr(sys, 'argv', ['bml', 'track', str(sub)])
    cli.main()
    capsys.readouterr()

    monkeypatch.setattr(sys, 'argv', ['bml', 'track', str(base)])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    out = capsys.readouterr().out
    assert "nested under" in out and str(sub) in out
    assert exc.value.code == 1


def test_nested_guardrail_child_direct(monkeypatch, tmp_path, capsys):
    # Track a parent first, then error when tracking its subfolder directly
    base = tmp_path / "base"
    sub = base / "subdir"
    sub.mkdir(parents=True)
    import blackmirror_lite.watcher as watcher
    monkeypatch.setattr(watcher, 'start_watch', lambda path: None)
    monkeypatch.setattr(sys, 'argv', ['bml', 'track', str(base)])
    cli.main()
    capsys.readouterr()

    monkeypatch.setattr(sys, 'argv', ['bml', 'track', str(sub)])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    out = capsys.readouterr().out
    assert "already under tracked folder" in out and str(base) in out
    assert exc.value.code == 1