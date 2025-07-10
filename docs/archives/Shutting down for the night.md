codex
Below is how to get back on solid ground under WSL/Windows, plus confirmation that we now preserve your Git metadata by default, and a quick
smoke‑test recipe. Once you’ve exercised this a bit, we can circle back on the .exe and auto‑updater discussion.

---

## 1️⃣ WSL path handling

Under WSL your Windows drives are mounted under /mnt. The tool expects POSIX‑style paths under Linux, so instead of:

    # ❌ This won’t work in WSL:
    bml track C:\ADAPTiQ_SaaS\ADAPTiQ

use the corresponding Linux path:

    # ✅ Run inside WSL:
    bml track /mnt/c/ADAPTiQ_SaaS/ADAPTiQ

If you prefer a pure‑Windows shell (PowerShell or CMD), you can run the same command natively there:

    # ✅ Run in PowerShell/CMD:
    bml track C:\ADAPTiQ_SaaS\ADAPTiQ

---

## 2️⃣ Default preservation of .git & .env

You were right: messing with a project’s Git folder would be disastrous. We’ve updated the rollback engine so that .git and .env are always
kept—you no longer need to pass --keep .git .env every time.

    # See the help text now mentions it by default…
    bml jump-back --help

Under the hood, we prepend ['.git', '.env'] to whatever you pass in --keep.

---

## 3️⃣ Where to find your snapshots

By default BlackMirror‑Lite places its JSONL store outside your project so it won’t be deleted if you remove your code folder:

┌─────────────────────────────┬──────────────────────────────────────────────────────────┐
│ Platform                    │ Store Location                                           │
├─────────────────────────────┼──────────────────────────────────────────────────────────┤
│ Linux/macOS                 │ ~/.blackmirror_lite/mirrors/                              │
├─────────────────────────────┼──────────────────────────────────────────────────────────┤
│ Windows & WSL               │ %LOCALAPPDATA%\blackmirror_lite\mirrors\                │
│                             │ (/mnt/c/Users/<YourUser>/AppData/Local/blackmirror_lite/mirrors/) │
└─────────────────────────────┴──────────────────────────────────────────────────────────┘

You can browse that folder to inspect per‑file logs (one `.jsonl` per tracked file).

---

## 4️⃣ Quick smoke‑test recipe

    1. **Ensure no tracked folders:**

           bml list
           # (should print “No tracked folders.”)
    2. **Track your repo/project:**

           bml track /mnt/c/ADAPTiQ_SaaS/ADAPTiQ
    3. **In another shell, start the watcher:**

           bml watch

       You should see output like:

           [INFO] Watching /mnt/c/ADAPTiQ_SaaS/ADAPTiQ
    4. **Create or edit a file inside that folder:**

           echo hello >> /mnt/c/ADAPTiQ_SaaS/ADAPTiQ/hello.txt

       The watcher shell should log:

           [Modified] hello.txt
    5. **Back in the first shell, roll back 1 minute:**

           bml jump-back 1m

       Your `hello.txt` will revert to the state it had one minute ago, and your `.git`/`.env` folders remain untouched.
    6. **Verify snapshots on disk:**

           ls ~/.blackmirror_lite/mirrors/hello.txt.jsonl
           tail -n2 ~/.blackmirror_lite/mirrors/hello.txt.jsonl

---

### All tests are passing

    # In your virtualenv (or env/):
    pip install pytest
    pytest -q --disable-warnings --maxfail=1
    # → 10 passed in ~0.2s

---

## What’s next?

    * Play with the watcher/jump‑back cycle a few times on your laptop.
    * Make sure the WSL note and default `.git`/`.env` protection feel right.

Once you’ve exercised it end‑to‑end, we can dive into packaging a standalone Windows .exe and an auto‑updater (Sprint 7). That would be an
easy extension with PyInstaller (and a small online‑version‑check helper), but let’s save it until we’ve stress‑tested the core.

Let me know how this goes!

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
ctrl+c to exit | "/" to see commands | enter to send — 98% context left
