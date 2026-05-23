## Why

All feature development (upload, stem separation, mixer) depends on a working project skeleton. Without a monorepo baseline — shared tooling, environment configuration, and a running dev server for both apps — no meaningful vertical slice can be built or tested.

This is Phase 1 groundwork: get the repo runnable before adding any product logic.

## What Changes

- New `/apps/web` — React + TypeScript app bootstrapped with Vite, TailwindCSS configured
- New `/apps/api` — Python FastAPI app with a health-check endpoint
- Root-level shared environment configuration (`.env.example`, env loading conventions)
- `package.json` at root for frontend workspace tooling
- `requirements.txt` (or `pyproject.toml`) in `/apps/api`
- Basic `README.md` explaining how to run both apps locally

## Capabilities

### New Capabilities

- `monorepo-foundation`: Root repo structure, workspace configuration, shared `.env` conventions, and dev tooling scripts that let both apps start with a single command

### Modified Capabilities

<!-- None — this is the initial scaffolding; no existing specs to change -->

## Non-goals (MVP scope)

- Docker / containerization — not needed at this stage
- CI/CD pipeline setup — future phase
- Authentication, database, or queue wiring — Phase 3
- Deployment configuration (Vercel, Railway) — Phase 4
- Any product features (upload, mixer, export) — later changes

## Impact

- Creates the root directory structure all future changes will build on
- Establishes `.env` naming conventions that backend and frontend will share
- No existing code affected (greenfield)
