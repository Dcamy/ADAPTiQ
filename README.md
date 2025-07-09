# 🪞 BlackMirror Lite

**Your repo will never die again.**  
This is a zero-IQ failsafe. It watches your files and saves every version as a JSONL log — no Git, no setup, just **paranoia made portable**.

## Why?

Codex deleted my life's work.  
Then I rebuilt it. Then it deleted the rebuild.  
So I built this.

## Usage

```bash
python blackmirror_lite.py /path/to/project
```

Every time you hit save, it logs the full file in:

```
~/.blackmirror_lite/<your-project>/path/to/file.jsonl
```

Each line has a timestamp and the full file content. Think Git on god mode, no commits.

## Want it to auto-start on boot?

Run:

```bat
install_autostart.bat
```

More coming soon from the **ADAPTiQ** stack.

## License

MIT — just don't sell it to the same AI that killed my repo.

````

---

## ✅ GitHub Public Launch

Push to:
```bash
git@github.com:Dcamy/ADAPTiQ.git
````

Use branch `blackmirror-lite` if keeping trunk clean.
