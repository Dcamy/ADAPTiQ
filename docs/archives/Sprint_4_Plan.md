# Sprint 4 — Next Feature Plan

This sprint focuses on improving `jump-back` scoping, introducing convenient commands, update notifications, and mirror-store guardrails:

## 1. Scoped rollback (`jump-back`)

- **Default behavior**: `bml jump-back <delta>` rolls back only the _current working directory_ (CWD), not all tracked roots.
- **Path argument**: allow `bml jump-back <delta> <path>` to target a specific folder or file.
- **Per-file option**: support `--only <file>` to limit rollback to named files within the path.

## 2. `bml track me`

- Shortcut to track the current directory (`$PWD`).
- **Guardrails**: refuse to track if the CWD is nested under an existing tracked root (or vice versa) to avoid double‑watching.

## 3. `bml update` with desktop notifications

- Check for new version updates:
  - If installed via PyPI or pipx: query PyPI or the GitHub Releases API for the latest published version.
  - If running from a Git clone: detect the local `.git` folder and compare `origin/main` vs local HEAD.
- If an update is available, invoke `pip install --upgrade blackmirror_lite` or `pipx upgrade blackmirror-lite` (as appropriate).
- Notify the user via desktop notification using `plyer` (cross‑platform: Windows, macOS, Linux).

## 4. Mirror-store size warning

- On startup or via `bml status`, if the mirror store exceeds a configurable threshold (default 10 GB), print a warning:
  "⚠️ Mirror store >10 GB. Consider running `bml prune --max-size 10G` or tighten your `.bmlignore`."

## 5. Nested-track guardrails

- Prevent `bml track` (and `bml track me`) from adding a root that is a subdirectory of any existing tracked folder—and vice versa.
- Provide clear error messages explaining the conflict.

---

**Deliverables by end of Sprint 4:**

| Feature                     | Deliverable                                          |
| --------------------------- | ---------------------------------------------------- |
| Scoped rollback             | CLI parsing for CWD default, `<path>`, and `--only`  |
| `bml track me`              | New command + nesting checks                         |
| `bml update` notifications   | Update checker + `plyer` integration                 |
| Store-size warning          | Alert on store size > threshold in status/startup    |
| Nested-track guardrails     | Refuse ambiguous track requests with user guidance   |

*End of Sprint 4 Plan*