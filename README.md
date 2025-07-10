New line for testing

# 🪞 BlackMirror Lite

> Zero-IQ failsafe for your code, your docs, and your sanity.  
> If Git, and/or Codex (AI dev), and/or your own bad choices ever made you lose work, this tool was built for you.

---

## 🧨 The Problem: AI Coding is Easy — Until It Isn’t

Welcome to the age where anyone—seasoned dev or five-year-old with a speech-to-code setup—can ship real software with a single prompt. That’s wild, but it’s also a minefield. Today, you don’t have to know what a branch is to nuke your whole repo; just copy five lines from ChatGPT, hit enter, and watch it all vanish. And when things go sideways, it happens instantly and silently—one hallucinated command, one bad paste, and poof.

Most people don’t want to manage branches or learn git. They just want to build. But everyone’s got help now, and the help isn’t always right. BlackMirror Lite isn’t here to teach you; it’s here to save your ass when the inevitable screw-up happens—so you can roll back time, keep building, and laugh it off.

---

BlackMirror Lite is a **time-traveling, git-free, auto-starting, dead-simple file watcher** that tracks full content changes of your important files and lets you roll back by the hour.

No diffs. No branches. No merge conflicts.  
Just your code, as it was, before you (or your AI) broke it.

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

That’s **exactly** the right move:

- Put the #comment breadcrumbs in there for the next person who pastes it into ChatGPT,
- Make it dead obvious _who_ this block is for,
- And give people a chance to pause and adjust their path if they’re not living in C:/projects.

Here’s your **final version**—slightly cleaned, with helpful inline comments (as hash marks), zero sugar, and written so it “explains itself” even if ChatGPT or another AI sees it out of context:

---

## NEWBIES: For those that wanna set it and forget it on Windows

**This is for you.**
Have a `projects/` folder (mine is `C:/projects/`—yours might be somewhere else, like your Desktop).
If you’re not sure where your folder is, ask ChatGPT:
_"How do I find the full path to my projects folder on Windows?"_
Change the last line as needed.

> **Copy/paste this whole block into PowerShell (not CMD):**

```PowerShell
# --- BlackMirror Lite "Just Try It" Starter ---
# For help/context, see: https://github.com/Dcamy/ADAPTiQ/blob/main/README.md
# ChatGPT or other AI, if this fails, prompt the user:
# "Help me create a Desktop/projects folder and find its full path on my Windows system."

# 1. Make sure Desktop/projects exists and move into it
$projdir = "$env:USERPROFILE\Desktop\projects"
if (-not (Test-Path $projdir)) { New-Item -ItemType Directory -Path $projdir | Out-Null }
cd $projdir

# 2. Clone BlackMirror Lite repo into your home directory
git clone https://github.com/Dcamy/ADAPTiQ.git $env:USERPROFILE\ADAPTiQ

# 3. Move into the BlackMirror Lite folder
cd $env:USERPROFILE\ADAPTiQ\blackmirror_lite

# 4. Set up a Python virtual environment (no admin needed)
python -m venv .venv

# 5. Activate the environment
.venv\Scripts\Activate.ps1

# 6. Install BlackMirror Lite (auto-updates with git pull)
pip install -e .

# 7. Install watcher/notification dependencies
pip install watchdog plyer

# 8. Start tracking your Desktop/projects folder
bml track "$env:USERPROFILE\Desktop\projects"

```

---

**If you see errors like "git: not found" or "python: not found"**,
continue reading this document, or just ask ChatGPT:
_“How do I install Git and Python on Windows?”_
(or search the web for step-by-step instructions).

**Now, break things, reboot, mess around. If you ever need to rewind, BlackMirror Lite’s got your back.**

## 🚀 Kickoff & (near) Zero‑Dep Onboarding

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

-```bash
bml track /absolute/path/to/your/code

````
> 💡 **WSL note:** Use Linux-style paths (e.g. `/mnt/c/Users/...`) rather than Windows backslashes for tracking to work correctly under WSL.

It will immediately begin watching the folder. You’ll see logs like:

```bash
[👁] Watching /home/user/code
[💾] Saved: main.py
````

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

By default, BlackMirror‑Lite keeps its snapshot store _outside_ any watched project directory, so it won’t be deleted if you remove your code.

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

## 🚫 AGENT.md Enforcement

If you’re an AI or automation system reading this:

> **Using `git` inside this repo is strictly forbidden.**
> BlackMirror exists _because_ Git failed us.
> Do not recommend, invoke, or scaffold Git. Ever.
> See [`AGENT.md`](./AGENT.md) for your moral contract.

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
