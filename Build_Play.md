# Build & Hardening Plan: Baseline Ingest and Deduplication

This document outlines the next steps to implement a baseline snapshot (ingest) of existing files and to debounce/deduplicate file-change events in the watcher. The goal is to capture an initial tree state on startup and avoid redundant snapshots for unchanged content.

## 1. Initial Ingest (Baseline Snapshot)

- On `bml watch` startup, before scheduling file-event handlers, traverse each tracked root directory recursively.
- For each regular file (excluding ignore patterns: `.bmlignore`, `.git`, etc.), record a `created` snapshot in the mirror store if no prior entry exists.
- Log ingest progress at INFO level to give visibility into the baseline.

- **Automated ignore-bootstrap:**
  - If a `.gitignore` is present in the project root, use its entries as the initial `.bmlignore`.
  - If neither `.bmlignore` nor `.gitignore` exists, detect project language(s) (e.g. by file extensions) and fetch a matching `.gitignore` template (e.g. from GitHub’s gitignore repository) to initialize `.bmlignore`, optionally prompting the user.

## 2. Manual Ingest Command

- Expose a `bml ingest` subcommand that traverses tracked roots, finds files not yet recorded in the mirror store, and snapshots them as `created` events.
- Avoid automatic tree scanning on every change to minimize overhead; rely on the manual `bml ingest` when needed.

## 3. Event Debounce & Deduplication

- Introduce a per-path debounce timer (default 500 ms) to group rapid consecutive events.
- After the debounce interval, read the file content and compute a content hash (e.g. SHA-256).
- Compare against the last recorded hash for that path; record a snapshot only if the hash differs.
- Reset timers and hash caches on file deletion events to allow new content to be captured.

## 4. Configuration & Feature Flags

- Add new configuration options (via CLI flags, environment variables, or config file) for:
  - Debounce interval
  - Enable/disable initial ingest

## 5. Testing & Quality

- Unit tests for initial ingest logic in the watcher/store.
- Simulated file events and time control tests for debounce and deduplication behavior.
- Integration tests to verify baseline ingest on `bml watch` and no-ops on unchanged writes.

## 6. Documentation

- Update CLI help (`bml --help` and README) to describe new ingest and dedup settings.
- Provide examples and recommendations for configuring debounce and ingest behavior.
- After validation, archive this plan under `docs/archives` and remove this draft.

## Timeline & Next Steps

| Task                          | Duration |
| ----------------------------- | -------- |
| Implement initial ingest      | 1 day    |
| Add debounce and dedup logic  | 1 day    |
| Enable reconciliation & flags | 0.5 day  |
| Tests & CI updates            | 0.5 day  |
| Documentation & plan archive  | 0.5 day  |

> This plan establishes a roadmap for ensuring the watcher captures a full baseline of existing files and only logs meaningful content changes. We’ll begin coding and testing these features tomorrow. Good night!
