## 🧠 **Back to Basics — BlackMirror Lite: 5–10 User Stories**

These are short, focused user scenarios that ground the product. Use them to lock MVP scope and build only what actually matters.

---

### 🔐 1. **As a developer, I want to track my code folder so that I never lose work again.**

- User runs `python blackmirror_lite.py ~/myproject`
- Tool silently watches all changes
- Writes timestamped versions somewhere safe
- Crash or bad commit? Rollback.

---

### 🧙 2. **As a chaotic coder, I want to jump back in time and undo the last 2 hours.**

- User runs:
  `python -m blackmirror_lite jump-back 2h`
- Everything rolls back to how it was at that time.
- Like Git time travel **without needing Git**.

---

### 🤖 3. **As a Zero IQ user, I want it to run forever after I install it once.**

- First run:
  `python blackmirror_lite.py ~/code`
  → prompts: "Install autostart?"
  → installs a boot task
  → never thinks about it again

---

### 🗂 4. **As a multitasker, I want to track multiple folders.**

- Tracks `/code`, `/obsidian`, `/side_project`
- One mirror log per tracked dir
- All managed from `~/.blackmirror_lite`

---

### 🧪 5. **As a tweaker, I want to jump back just one file, not the whole system.** _(stretch)_

- CLI:
  `jump-back 1h --only blackmirror_lite.py`

---

### 🧹 6. **As a cautious dev, I want to keep my `.git` and `.env` untouched when jumping back.**

- CLI:
  `jump-back 3h --keep .git .env`

---

### 📝 7. **As a user, I want to see which folders are being tracked.**

- CLI: `blackmirror_lite list`
  → prints each tracked root

---

### 🧼 8. **As a clean freak, I want to untrack a folder I no longer care about.**

- CLI: `blackmirror_lite untrack ~/obsidian`

---

### 🧰 9. **As a power user, I want to install BlackMirror Lite system-wide via pipx.** _(post-MVP)_

- One-liner:
  `pipx install blackmirror-lite`
  → gets `bml` CLI command

---

### 📦 10. **As a dev team, I want to package BlackMirror Lite into a VS Code extension or installer.** _(later)_

- But today? Just keep it a single file.

---

## ✅ MVP Must-Have Stories

If you just shipped these, you're winning:

- \#1 — track folder
- \#2 — jump-back
- \#3 — autostart
- \#4 — track multiple
- \#6 — `--keep` safe files
- \#7 — list tracked
# User Stories

Below are typical usage scenarios illustrating why BlackMirror Lite is helpful.

## Story 1: Recover from accidental deletion
Alice accidentally deletes a critical source file. With BlackMirror Lite running in the background, she simply executes:

```bash
bml jump-back 2m
```

Her deleted file is restored exactly as it was two minutes ago—no Git required.

## Story 2: Undo AI-generated refactoring gone wrong
Bob uses an AI assistant that refactors code but introduces bugs. Forgetting to commit, he runs:

```bash
bml jump-back 5m --keep config.yaml
```

This command rewinds his code changes while preserving configuration files.

## Story 3: Protect secrets during rollback
Ciara stores secrets in `.env` files. To roll back code without touching sensitive files, she uses:

```bash
bml jump-back 1h --keep .env credentials.json
```

Her secret files remain intact while all other project files rewind.

## Story 4: Always-on snapshotting
Dan sets up autostart on his machine so BlackMirror Lite launches on boot. Even if he breaks critical files overnight, he can recover his work the next morning without manual startup.