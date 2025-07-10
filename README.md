New line for testing

# 🪞 BlackMirror Lite

> Zero-IQ failsafe for your code, your docs, and your sanity.  
> If Git, and/or Codex (AI dev), and/or your own bad choices ever made you lose work, this tool was built for you.

---

### Delta Format Cheat Sheet

| Format | Meaning    |
| ------ | ---------- |
| `12s`  | 12 seconds |
| `30m`  | 30 minutes |
| `2h`   | 2 hours    |
| `1d`   | 1 day      |

---

### Usage Examples

#### For Seasoned Devs (Fast Lane)

| Command                           | Description                             |
| --------------------------------- | --------------------------------------- |
| `bml jump-back 2h`                | Roll back current directory by 2 hours  |
| `bml jump-back 30m /path/to/proj` | Roll back `/path/to/proj` by 30 minutes |

#### For Newcomers (Copy & Paste)

```bash
# Roll back current directory by 2 hours, preserving .git and .env
bml jump-back 2h --keep .git .env
```

## 🧨 The Problem: AI Coding is Easy — Until It Isn’t

Welcome to the age where anyone—seasoned dev or five-year-old with a speech-to-code setup—can ship real software with a single prompt. That’s wild, but it’s also a minefield. Today, you don’t have to know what a branch is to nuke your whole repo; just copy five lines from ChatGPT, hit enter, and watch it all vanish. And when things go sideways, it happens instantly and silently—one hallucinated command, one bad paste, and poof.

Most people don’t want to manage branches or learn git. They just want to build. But everyone’s got help now, and the help isn’t always right. BlackMirror Lite isn’t here to teach you; it’s here to save your ass when the inevitable screw-up happens—so you can roll back time, keep building, and laugh it off.

---

BlackMirror Lite is a **time-traveling, auto-starting, dead-simple file watcher** that tracks full content changes of your important files and lets you roll back by the hour, minuet or second.

No diffs. No branches. No merge conflicts.  
Just your code, as it was, before you (or your AI) broke it.

## Install

**_🧠 For the Newbies to Development_**

- cd to your projects/ folder (or whatever you use... I call mine C:/ not wise but I like it)
- ensure you have a environment set up, if you dont know what that means ask a model to walk you through it

```Bash
git clone https://github.com/Dcamy/ADAPTiQ.git
cd ADAPTiQ
pip install watchdog
pip install -e .
bml install-autostart
```

**_🧠 For the Devs_**

- Read the docs and CTRL + C what you need/want from above.

---

## ✅ Features

- 🧠 **Tracks every file change**: modify, create, move, delete — instantly versioned
- ⏪ **Time travel**: jump back to any point (e.g. `jump-back 2h`)
- 🔐 **Safe by default**: `.git`, `.env`, and other sensitive files are always preserved on rollback
- 🧃 **Zero IQ-friendly**: Just run it once — it auto-starts after reboot
- 🧰 **One file, one install**: No services, no database, no dependencies beyond `watchdog`
- 🚨 **Mirror-store size warning**: alerts when your snapshot store grows beyond the configured threshold (default 10 GB)
- 🦺 **No Git. Ever. Lost.**: That’s the point.

---

| Task                             | Installed CLI (`bml`)                                |
| -------------------------------- | ---------------------------------------------------- |
| Track current directory          | `bml track me`                                       |
| Track a specific folder          | `bml track /path/to/folder`                          |
| Stop tracking a folder           | `bml untrack /path/to/folder`                        |
| Show tracked folders             | `bml list`                                           |
| Run the watcher (manual)         | `bml watch`                                          |
| Enable autostart on login/boot   | `bml install-autostart`                              |
| Show status and recent actions   | `bml status`                                         |
| Roll back by time delta          | `bml jump-back <delta>`                              |
| Limit rollback to specific files | `bml jump-back <delta> --only <file> [glob ...]`     |
| Jump back and keep files         | `bml jump-back <delta> --keep <paths>`               |
| Prune snapshots by age or size   | `bml prune [--keep-days <days>] [--max-size <size>]` |
| Run self-contained demo (verify) | `bml prove-it`                                       |
| Check for new versions           | `bml update`                                         |

---

## 💾 Where are files stored?

By default, BlackMirror‑Lite keeps its snapshot store _outside_ any watched project directory, so it won’t be deleted if you remove your code.

Please confirm this location, I think it changed

- **Linux/macOS**: `~/.blackmirror_lite/mirrors/`
- **Windows & WSL**: `%LOCALAPPDATA%\\blackmirror_lite\\mirrors\\`

---

## 📝 Known issues & TODO

Before recommending BlackMirror Lite for general use, consider tackling these important hardening tasks. Community PRs welcome!

- **Improve log filename encoding** to avoid collisions and handle special characters instead of the current `__` replacement.
- **Harden rollback deletion logic**: only delete when a prior snapshot exists and offer a `--dry-run` preview mode.
- **Support file moves/renames** in the watcher so history continuity is preserved.
- **Embed schema and tool version metadata** in each JSONL snapshot entry for future-proof migrations.
- **Add a non-interactive flag** (e.g. `--yes`) to `bml install-autostart` to support headless or scripted installs.
- **Extend `bml update` for Git clones**: detect local Git checkouts and suggest `git pull` when upstream differs.
- **Debounce or dedupe identical snapshots** generated in rapid succession to reduce log bloat.
- **Provide a `bml verify` command** to detect and repair corrupted, orphaned, or inconsistent log files.

  (in WSL, this maps to `/mnt/c/Users/<YourUser>/AppData/Local/blackmirror_lite/mirrors/`)

Each tracked file has its own `.jsonl` log. Every change is recorded in full, timestamped.
It’s your own local time machine.

---

## ⏳ How does rollback work?

You can jump back to any point in time—and by default it only affects the current working directory:

```bash
# Roll back this folder to how it was 2 hours ago
bml jump-back 2h

# Or target another directory or file directly:
bml jump-back 2h /path/to/project

# Limit rollback to specific files under that path:
bml jump-back 2h /path/to/project --only main.py docs/*.md
```

If you omit the path, `bml jump-back` uses the current directory (which must be under a tracked folder). You can also restrict to individual files via `--only`.

Want to protect additional files? ('.git' and '.env' are always preserved)

```bash
bml jump-back 3h --keep .git .env
```

This leaves those untouched while rolling back the rest.

---

## 🧪 Testing

We use `pytest` for unit and integration tests. To run the full test suite:

```bash
pip install pytest
pytest
```

## 📡 Future Features (Not Yet in Lite)

- Per‑file rollback (`jump-back --only file.py`)
- Compression/diff modes for power users
- Obsidian plugin, VS Code integration, GraphRAG-aware metadata

---

## 🧙 Who is this for?

- Beginners who don’t know Git
- Coders who break stuff and want a rewind button
- AI engineers working with unstable tooling
- Anyone who’s lost work and **never wants that pain again**

---

## 📉 Pruning & Ignoring files

To prevent unbounded disk growth, BlackMirror Lite now supports:

- **Ignore patterns**: add a `.bmlignore` file in your tracked folder with glob patterns (one per line) to skip snapshotting matching paths (comments with `#` allowed).
- **Pruning**: age-based or size-based cleanup of your mirror store:
  ```bash
  bml prune --keep-days 7      # drop snapshots older than 7 days
  bml prune --max-size 5G      # keep total store size under 5 GiB
  ```

These tools let you control which files are logged and how long snapshots are retained.

## 🧠 Philosophy

> “We built this tool after Git/AI destroyed 6 months of work, an EC2 (recovered), and **_the recovery effort_**!
>
> > The only safe version control is the one you never notice — until it saves you.”

This is the **Git-failsafe**. You can thank it later.

---

MIT License.
Built by [ADAPTiQ](https://github.com/Dcamy) in sheer frustration.
