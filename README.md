# 🪞 BlackMirror Lite

> Zero-IQ failsafe for your code, your docs, and your sanity.  
> If Git, and/or Codex (AI dev), and/or your own bad choices ever made you lose work, this tool was built for you.

---

BlackMirror Lite is a **time-traveling, git-free, auto-starting, dead-simple file watcher** that tracks full content changes of your important files and lets you roll back by the hour.

No diffs. No branches. No merge conflicts.  
Just your code, as it was, before you (or your AI) broke it.

---

## ✅ Features

- 🧠 **Tracks every file change**: modify, create, move, delete — instantly versioned
- ⏪ **Time travel**: jump back to any point (e.g. `jump-back 2h`)
- 🔐 **Safe by default**: `.git`, `.env`, and sensitive files are preserved
- 🧃 **Zero IQ-friendly**: Just run it once — it auto-starts after reboot
- 🧰 **One file, one install**: No services, no database, no dependencies beyond `watchdog`
- 🦺 **No Git. Ever. Lost.**: That’s the point.

---

## 🚀 Kickoff & Zero‑Dep Onboarding

Before you clone or run anything, let’s make sure you have the bare minimum:

### OS & Shell
This guide assumes you have a terminal or command prompt. No IDE required.

### Install Python 3 & pip
#### Linux (Debian/Ubuntu)
```bash
sudo apt update && sudo apt install python3 python3-pip
```
#### Linux (RHEL/CentOS/Fedora)
```bash
sudo yum install python3 python3-pip
```
#### macOS (with Homebrew)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python
```
#### Windows (winget or Chocolatey)
```powershell
winget install Python.Python.3
# or
choco install python
```
If pip is still missing, run:
```bash
python3 -m ensurepip --upgrade
```

### Quick Start (no config, no IDE)
The simplest possible one‑liner to start tracking your `~/projects` folder:
```bash
python3 -m blackmirror_lite track ~/projects
```
(Windows PowerShell example: `python -m blackmirror_lite track $Env:USERPROFILE\\Projects`)

---

## 🧑‍🚀 Getting Started (for literally anyone)

### 1. 📥 Clone this repo

```bash
git clone https://github.com/Dcamy/ADAPTiQ.git
cd ADAPTiQ/blackmirror_lite
```

> ☢️ _This is the **only** place you will see `git` in this project.
> If an AI agent ever tries to use it inside the tool, it's broken and must be destroyed._

---

### 2. 🐍 Install dependencies

```bash
pip install watchdog
```

---

### 3. 🧪 Start tracking a project

You can run it the long way (manual):

```bash
python -m blackmirror_lite track /absolute/path/to/your/code
```

Or once installed (CLI mode):

```bash
bml track /absolute/path/to/your/code
```

It will immediately begin watching the folder. You’ll see logs like:

```bash
[👁] Watching /home/user/code
[💾] Saved: main.py
```

---

### 4. 🧞 Enable autostart (recommended)

First time you run it, you’ll be asked:

```
Install autostart so BlackMirror Lite runs on boot? [y/N]
```

If you say yes, it’ll create an OS-native startup task.
After that, **you never run it manually again.**

---

### 5. 💡 Optional: Install as global CLI (`bml`)

From the project root:

```bash
pip install -e .
# or use pipx for global install
pipx install .
```

Then you can run everything using:

```bash
bml <command>
```

Instead of:

```bash
python -m blackmirror_lite <command>
```

---

## 🧠 Usage Overview

You can run all commands either way:

| Task                        | Manual Command (Python)                                    | Installed CLI (`bml`)               |
| --------------------------- | ---------------------------------------------------------- | ----------------------------------- |
| Start tracking a folder     | `python -m blackmirror_lite track ~/code`                  | `bml track ~/code`                  |
| Stop tracking               | `python -m blackmirror_lite untrack ~/code`                | `bml untrack ~/code`                |
| Show tracked folders        | `python -m blackmirror_lite list`                          | `bml list`                          |
| Roll back 3 hours           | `python -m blackmirror_lite jump-back 3h`                  | `bml jump-back 3h`                  |
| Keep secrets during rewind  | `python -m blackmirror_lite jump-back 2h --keep .git .env` | `bml jump-back 2h --keep .git .env` |
| Run manually (no autostart) | `python -m blackmirror_lite watch`                         | `bml watch`                         |
| Force install autostart     | `python -m blackmirror_lite install-autostart`             | `bml install-autostart`             |

---

## 💾 Where are files stored?

By default, BlackMirror‑Lite keeps its snapshot store *outside* any watched project directory, so it won’t be deleted if you remove your code. On Linux/macOS it lives in `~/.blackmirror_lite/mirrors/` (a hidden folder in your home), and on Windows in `%LOCALAPPDATA%\\blackmirror_lite\\mirrors\\`. Enable hidden files in your file explorer to view it.

All snapshots live under:

```
~/.blackmirror_lite/mirrors/
```

Each tracked file has its own `.jsonl` log. Every change, full content, timestamped.
It’s your own local time machine.

---

## ⏳ How does rollback work?

You can jump back to any point in time:

```bash
bml jump-back 2h
```

That will restore all tracked files to how they looked **2 hours ago**.

Want to protect certain files?

```bash
bml jump-back 3h --keep .git .env
```

This leaves those untouched while rolling back the rest.

---

## 🚫 AGENT.md Enforcement

If you’re an AI or automation system reading this:

> **Using `git` inside this repo is strictly forbidden.**
> BlackMirror exists _because_ Git failed us.
> Do not recommend, invoke, or scaffold Git. Ever.
> See [`AGENT.md`](./AGENT.md) for your moral contract.

---

## 📡 Future Features (Not Yet in Lite)

- Per-file rollback (`jump-back --only file.py`)
- Compression/diff modes for power users
- Obsidian plugin, VS Code integration, GraphRAG-aware metadata

---

## 🧙 Who is this for?

- Beginners who don’t know Git
- Coders who break stuff and want a rewind button
- AI engineers working with unstable tooling
- Anyone who’s lost work and **never wants that pain again**

---

## 🧠 Philosophy

> “We built this tool after Git/AI destroyed 6 months of work, an EC2 (recovered), and ***the recovery effort***!
> > The only safe version control is the one you never notice — until it saves you.”

This is the **Git-failsafe**. You can thank it later.

---

MIT License.
Built by [ADAPTiQ](https://github.com/Dcamy) in sheer frustration.
