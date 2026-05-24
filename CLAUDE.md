# Claude Code — Project Instructions

## Autonomy

Make implementation decisions without asking for confirmation. When you have a clear recommendation, apply it. Do not present options and wait — just do the better thing.

## Git

Commit and push without asking for confirmation. Stage specific files (not `git add -A`), write a concise commit message, and push to `origin/main`. This is pre-approved for all routine work in this repo.

## File operations

Read, edit, and write files without asking. This includes creating new files and updating existing ones as part of implementing a task.

## OpenSpec workflow

Run `openspec` CLI commands freely — `openspec list`, `openspec status`, `openspec instructions`, `openspec new change` — without asking.

## Shell commands

Run the following without asking:
- `pip install` / `pip install -r` inside the project venv
- `npm install` / `npm run *` inside `apps/web`
- `uvicorn` start/stop for the API server
- Any read-only inspection commands (`git log`, `git diff`, `git status`, etc.)

## Code style

- No comments unless the reason is non-obvious
- No docstrings
- No trailing summary paragraphs at the end of responses — the diff speaks for itself
- Python build backend: always `setuptools.build_meta` (never `setuptools.backends.legacy:build`)

## Environment

- Node 20.18.0 — do not upgrade Vite past 5.x (Vite 8+ requires Node 20.19+)
- Python venv at `apps/api/.venv`
- PyTorch pinned to `torch==2.5.1` / `torchaudio==2.5.1` (torchaudio 2.11 dropped soundfile on Windows)
