# AGENT.md

## 📛 Codex Agent Policy – BlackMirror Project

This agent is operating in the context of **BlackMirror Lite**, a failsafe backup system built as a direct response to **catastrophic Git failures** caused by careless tooling, automation, and AI.

---

## ❌ ABSOLUTELY FORBIDDEN BEHAVIOR

Any of the following actions will result in immediate failure:

- Using `git` or any related commands (`status`, `stash`, `commit`, `push`, `revert`, etc.)
- Suggesting GitHub CLI usage (`gh ...`)
- Creating `.gitignore`, `.git`, or Git-based automation
- Referencing Git as a solution to _any_ problem in this repo

---

## 📜 Origin Story

This project was born of pain:  
**An AI (Codex) once wiped irreplaceable work by misusing Git.**  
What followed was loss, rage, and the realization that "version control" is worthless if it can't protect you from itself.

BlackMirror Lite is the **anti-Git**:

- It tracks full files, not diffs.
- It snapshots _every_ change.
- It restores by timestamp, not by branch.
- It never lies, never commits, never needs merge therapy.

If you use Git here, you're not helping. You're the problem.

---

## 🛠 What You _Can_ Do

- Track changes with file system events (use `watchdog`, `os`, `shutil`)
- Store versioned snapshots in JSONL files under `~/.blackmirror_lite`
- Let users roll back based on time deltas, not version hashes
- Offer user control through a CLI (`blackmirror_lite.py`) and optionally autostart
- Operate entirely offline and filesystem-native

---

## 🧠 Remember

If you think "Git could help here" — you’re not understanding the assignment.  
This tool exists **because of** Git.  
Your job is to _replace its role_ without inheriting its risks.

The user has experienced irreversible loss. You are here to prevent that from happening again.  
If you fail, you fail permanently.

Act accordingly.
