# BlackMirror Lite – Shipping Sprint Plan

> This consolidated plan pulls together:

- The baseline WSL & smoke-test notes (Shutting down for the night.md)
- The next-milestone feature set (GPT4o_response.md)
- The disk-growth hardening strategy (our recent analysis)

---

## 1. Baseline Smoke Test & WSL Support

Establish a reliable foundation: get WSL path handling, default `.git`/`.env` protection, and the quick smoke-test workflow in place.

### 1.1 WSL Path Handling

Under WSL, Windows drives live under `/mnt`. Example:

```bash
# ❌ Won't work in WSL:
bml track C:\ADAPTiQ_SaaS\ADAPTiQ
# ✅ Use POSIX path inside WSL:
bml track /mnt/c/ADAPTiQ_SaaS/ADAPTiQ
```

【F:Shutting down for the night.md†L7-L23】

### 1.2 Default Preservation of `.git` & `.env`

`.git` and `.env` are always kept during rollback; users no longer need to pass `--keep` for them.

```bash
bml jump-back --help  # now mentions default preservation
```

【F:Shutting down for the night.md†L26-L35】

### ✅ **UPDATED SECTION: 1.3 Mirror Store Location**

BlackMirror snapshots are stored **outside of your project folders**, in a dedicated system directory, to ensure rollbacks are possible even if your codebase is deleted or corrupted.

```text
Linux/macOS/WSL:
  ~/.blackmirror_lite/mirrors/

Windows (native .exe or CMD/PowerShell):
  C:\Users\<YourUsername>\AppData\Local\blackmirror_lite\mirrors\
```

> 🧠 WSL Note: If you're running inside WSL, your mirror folder is in the Linux user's home, **not** on the Windows filesystem — even if you’re tracking `/mnt/c/...`.

You can view the mirror contents anytime with:

```bash
ls ~/.blackmirror_lite/mirrors/
```

Each tracked file is logged as a `.jsonl` snapshot log — full content, timestamped, one entry per change.

【F\:Shutting down for the night.md†L38-L51 ✅ REPLACEMENT】

---

### 🆕 **Section 1.3.1 Mirror Path Resolution Details** (📎 can be linked from status/advanced sections)

BlackMirror resolves the mirror storage location using this logic:

```python
if os.name == "nt":  # Windows native
    path = os.path.join(os.getenv("LOCALAPPDATA"), "blackmirror_lite", "mirrors")
else:
    path = os.path.expanduser("~/.blackmirror_lite/mirrors/")
```

If you’re running inside:

- **WSL** → Your data is stored under Linux home (`/home/<user>/.blackmirror_lite/...`)
- **Windows native Python or packaged `.exe`** → Uses the Windows user data path

These locations are **automatically created** on first run. You can safely browse them to see `.jsonl` logs per file:

```
<mirror_root>/mnt__c__MyProject__src__main_py.jsonl
```

Each file's log stores a full base64 snapshot for every change, unless excluded via ignore patterns.

【OPTIONAL INSERT: GPT4o_response.md, append to status or prove-it sections】

### 1.4 Quick Smoke-Test Recipe

```
1. bml list           # no tracked folders
2. bml track <proj>   # start tracking
3. bml watch          # launch watcher
4. echo hello >> hello.txt
5. bml jump-back 1m   # verify hello.txt rollback
6. ls ~/.blackmirror_lite/mirrors/*.jsonl
```

【F:Shutting down for the night.md†L54-L87】

👉 Add `ls ~/.blackmirror_lite/mirrors/` (already present)
✅ Suggest adding:

```bash
bml status  # view tracked folders + backup paths
```

### 1.5 Confirm Tests Pass

```
pip install pytest
pytest -q --disable-warnings --maxfail=1  # → 10 passed in ~0.2s
```

【F:Shutting down for the night.md†L89-L95】

### 1.6 What's Next (Post‑Smoke Test)

> After confirming the above, proceed to packaging a standalone Windows .exe and auto‑updater.
> 【F:Shutting down for the night.md†L98-L104】

---

## 2. Status & Self‑Proof Demo (Next Milestone)

Leverage the GPT4o team’s proposal to boost user trust before shipping core features.

### 2.1 `bml status`

Show per-folder status, mirror path, and recent actions:

```text
Tracking: /mnt/c/ADAPTiQ_SaaS/ADAPTiQ
Backups: ~/.blackmirror_lite/mirrors/mnt__c__ADAPTiQ_SaaS__ADAPTiQ
Last 3 actions:
[💾] 12:03:04 | snapshot | main.py (2.1 KB)
[💾] 12:03:11 | snapshot | worker.py (4.5 KB)
[📈] 12:03:21 | ignored  | logs/telemetry.db
```

【F:GPT4o_response.md†L7-L27】

#### 2.1 bml status

Add **mirror path resolution** logic to output, if not already reflected:

```text
Backups: ~/.blackmirror_lite/mirrors/mnt__c__ADAPTiQ_SaaS__ADAPTiQ
```

Maybe link:

> ℹ️ See “Mirror Path Resolution Details” in Section 1.3.1 for how this path is derived.

### 2.2 `bml prove-it`

Self‑contained demo of snapshot+rollback for first‑time users:

- Write `demo.py` → `print(1)`
- Wait & rewrite → `print(2)`, then `print(3)`
- Jump-back 3s, verify only `print(2)` remains
- Report PASS/FAIL with a friendly snark on failure
  【F:GPT4o_response.md†L30-L54】

### 2.3 Auto‑run Demo on First Launch

Detect empty mirror dir and run `prove-it` automatically:

```python
if not any(os.listdir(mirror_dir)):
    run_prove_it_demo()
```

【F:GPT4o_response.md†L57-L71】

### 2.4 Update `--help`

```text
  prove-it             Run a self-contained demo proving snapshot/rollback works
  status               Show tracking status, mirror paths, recent actions
```

【F:GPT4o_response.md†L75-L82】

### 2.5 TL;DR Implementation Plan

| Task                | Type     | Notes                                   |
| ------------------- | -------- | --------------------------------------- |
| `bml status`        | CLI      | Shows backup path + recent actions      |
| `bml prove-it`      | CLI demo | Creates + rolls back dummy changes      |
| Auto-run prove-it   | UX boost | Only on first install (no tracked dirs) |
| `--help` updates    | Polish   | Adds new verbs to help screen           |
| Issue link in error | UX/viral | Encourages feedback with style          |

【F:GPT4o_response.md†L86-L95】

---

## 3. Disk‑Growth Hardening

Mitigate unbounded JSONL growth by adding controls around what and how long we store:

1. **Ignore/Filter Support**: Skip unwanted files/dirs (e.g. `node_modules/**`, large binaries, `.git`, tool’s own mirrors).
2. **Retention/Pruning**: Add a `bml prune` command (`--keep-days`, `--max-size`) to trim or delete old snapshots.
3. **Large File Limits**: Warn/skip recording files above a configurable size threshold (e.g. >100 MB).
4. **Docs & Defaults**: Update README and build plan to document ignore lists, pruning, and size limits.

---

## 4. Packaging & .exe Distribution

Prepare a Windows executable and auto‑updater as the final shipping milestone:

**Sprint A**: Create PyInstaller spec, bundle `bml` CLI to `.exe`, verify on Win10/11.  
**Sprint B**: Integrate a minimal version‑check helper for auto‑updates (online metadata).  
**Sprint C**: Offer an MSI or install‑wizard, update README with `.exe` download instructions.

---

## 5. Sprint Roadmap

| Sprint | Goals                                              |
| ------ | -------------------------------------------------- |
| **1**  | Baseline WSL & smoke-test (Section 1)              |
| **2**  | Status & Self-Proof Demo (Section 2)               |
| **3**  | Disk-Growth Hardening (Section 3)                  |
| **4**  | Packaging & .exe Distribution (Section 4)          |
| **5**  | Final docs, polishing, integration tests & release |

---

_End of Shipping Sprint Plan_
