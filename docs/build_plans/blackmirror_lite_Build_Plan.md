# BlackMirror Lite Build Plan

This document lays out a sprint‑based roadmap for building BlackMirror Lite, starting with a zero‑dependency kickoff to meet users exactly where they are.

---

## Sprint 0 – Kickoff & Zero‑Dep Onboarding

**Goal**: Make the very first experience 100% free of assumptions. Users need only their OS and a terminal/command prompt. No IDE or preinstalled toolchain required.

### Deliverables
1. **OS Detection & CLI Instructions**
   - Detect Linux, macOS, or Windows and display appropriate shell instructions.
2. **Python 3 & pip Verification**
   - Check for `python3` (or `python` on Windows). If missing, guide users to install via package manager:
     - Linux: `sudo apt install python3 python3-pip` or `sudo yum install python3 python3-pip`
     - macOS: `brew install python` (with Homebrew install link if needed)
     - Windows: `winget install Python.Python.3` / `choco install python` or official installer link.
   - Ensure `pip3`/`pip` is available (`python3 -m ensurepip --upgrade`).
3. **One‑Line Project Tracking**
   - Provide a single, copy‑and‑paste command to begin watching a default `projects/` folder:
     ```bash
     python3 -m blackmirror_lite track ~/projects
     ```
     (Windows example: `python -m blackmirror_lite track %USERPROFILE%\Projects`)

4. **Standardized Mirror Store Location**
   - Define and document the default snapshot store path (OS‑specific, outside project folders) in the README, with instructions for viewing hidden files.

---

## Sprint 1 – Project scaffold & filesystem watcher

**Goal**: Establish the CLI entry point and basic change‑capture engine.

### Deliverables
- CLI scaffold (argparse or Click)
- `watchdog`‑based file event listener
- Append full‑content snapshots to per‑file JSONL logs in a standardized location outside tracked folders (e.g. `~/.blackmirror_lite/mirrors/` on Linux/macOS, `%LOCALAPPDATA%\\blackmirror_lite\\mirrors\\` on Windows)
- Console logging for tracking events

---

## Sprint 2 – Track / Untrack / List commands

**Goal**: Manage the set of watched folders.

### Deliverables
- `bml track <path>` / `untrack <path>` / `list` commands
- Persist tracked‑folders config (e.g. JSON file in `~/.blackmirror_lite`)

---

## Sprint 3 – Rollback engine (`jump-back`)

**Goal**: Restore a time‑delta snapshot of all tracked files.

### Deliverables
- Parse human‑friendly time deltas (e.g. `2h`, `30m`)
- Read JSONL logs and restore files to matching timestamp
- Implement `--keep` whitelist to preserve selected files

---

## Sprint 4 – Autostart / Daemon mode

**Goal**: Enable always‑on monitoring without manual launch.

### Deliverables
- One‑time prompt to install OS‑native startup task (systemd, launchd, Task Scheduler)
- `bml watch` for manual runs
- Ensure resilience across reboots

---

## Sprint 5 – Packaging & Install

**Goal**: Make BlackMirror Lite globally installable via pip.

### Deliverables
- `setup.py` or `pyproject.toml` with metadata
- Entry‑point script for `bml` CLI
- Instructions for `pip install -e .` and `pipx`

---

## Sprint 6 – Testing & Documentation

**Goal**: Solidify quality assurance and user docs.

### Deliverables
- Unit tests for watcher, snapshot store, rollback logic
- Integration smoke tests (e.g. demo folder rollback)
- Populate **USER_STORIES.md** from actual usage scenarios
- Update **README.md** with kickoff instructions, examples, and badges

---

## Future Features (post‑MVP)

- Downloadable binaries / zero‑install .exe, DMG, or equivalent
- Per‑file rollback (`jump-back --only <file>`) and subfolder targeting
- Compression/diff storage modes for power users
- Editor integrations (VS Code, Obsidian) and metadata plugins

---

*End of BlackMirror Lite Build Plan*