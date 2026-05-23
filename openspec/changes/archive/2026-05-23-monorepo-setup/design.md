## Context

Greenfield project. No existing code. The goal is to establish the repo structure that all future changes will build on — a React+TS frontend and a Python FastAPI backend, living side by side in a single repo, both runnable locally with minimal setup friction.

## Goals / Non-Goals

**Goals:**
- Reproducible local dev environment for both apps
- Consistent `.env` variable naming shared between frontend and backend
- Frontend dev server can reach the backend API (CORS configured for dev)
- Directory structure matches the layout defined in the project spec

**Non-Goals:**
- Docker or containerization
- CI/CD, linting pipelines, or pre-commit hooks
- Database, queue, or storage wiring
- Deployment configuration
- Any product features

## Decisions

### Frontend: Vite over Create React App
Vite has faster cold starts and HMR. CRA is deprecated upstream. Vite is the standard for new React+TS projects.

### Frontend package manager: npm workspaces (not pnpm/yarn)
Keeps setup friction low — no extra toolchain to install. A `package.json` at root with a `workspaces` field pointing at `apps/web` is sufficient for this stage.

### Backend dependency management: `pyproject.toml` + `pip`
More modern than a flat `requirements.txt`, plays well with virtual envs, and positions the project for future tooling (e.g. `uv`, `poetry`). A `venv` in `/apps/api` is the expected local setup.

### Single `.env.example` at repo root, per-app `.env` files
The root `.env.example` documents every variable used across the project. Each app reads only its own vars. This avoids secret leakage between apps while keeping a single source of truth for onboarding.

Naming convention:
- `VITE_API_BASE_URL` — frontend vars must be prefixed `VITE_` (Vite requirement)
- `API_HOST`, `API_PORT` — backend vars

### No monorepo orchestrator (Turborepo/Nx) yet
Overkill at this stage. A root `package.json` with two npm scripts (`dev:web`, `dev:api`) started via separate terminals is enough. Introduce Turborepo only when there are 3+ packages or shared build outputs to cache.

## Risks / Trade-offs

[CORS misconfiguration in dev] → FastAPI middleware configured to allow `http://localhost:5173` (Vite default). Document in README.

[Python venv not activated] → README must include explicit venv creation and activation steps; this is the #1 onboarding failure mode for Python projects.

[`.env` files committed accidentally] → `.gitignore` must include `.env` (not just `.env.local`) at both root and per-app level.
