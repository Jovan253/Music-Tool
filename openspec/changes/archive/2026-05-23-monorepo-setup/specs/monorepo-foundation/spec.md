## ADDED Requirements

### Requirement: Repo structure matches defined layout
The repository SHALL contain an `apps/web` directory for the React frontend and an `apps/api` directory for the FastAPI backend. No product code SHALL live outside these directories at this phase.

#### Scenario: Developer clones and inspects repo
- **WHEN** a developer clones the repo and lists the top-level contents
- **THEN** they see `apps/web/`, `apps/api/`, `.env.example`, and `README.md` at the root

### Requirement: Frontend app is runnable locally
The frontend SHALL be a Vite + React + TypeScript application. Running `npm run dev` inside `apps/web` (or `npm run dev:web` from root) SHALL start a local dev server at `http://localhost:5173`.

#### Scenario: Start frontend dev server
- **WHEN** the developer runs `npm install` then `npm run dev` from `apps/web`
- **THEN** Vite starts successfully and the browser shows a working React app at `http://localhost:5173`

#### Scenario: TypeScript compilation passes on fresh install
- **WHEN** the developer runs `npx tsc --noEmit` from `apps/web`
- **THEN** there are zero TypeScript errors

### Requirement: Backend app is runnable locally
The backend SHALL be a Python FastAPI application. After creating a virtual environment and installing dependencies, running `uvicorn main:app --reload` from `apps/api` SHALL start the API at `http://localhost:8000`.

#### Scenario: Start backend dev server
- **WHEN** the developer creates a venv, installs from `pyproject.toml`, and runs `uvicorn main:app --reload`
- **THEN** the server starts with no errors and listens on port 8000

#### Scenario: Health check endpoint responds
- **WHEN** a GET request is sent to `http://localhost:8000/health`
- **THEN** the response is `200 OK` with body `{"status": "ok"}`

### Requirement: Frontend can reach backend in development
The FastAPI backend SHALL have CORS configured to accept requests from `http://localhost:5173`. The frontend SHALL read the API base URL from the `VITE_API_BASE_URL` environment variable.

#### Scenario: Frontend fetches health check during development
- **WHEN** the frontend makes a fetch to `${VITE_API_BASE_URL}/health` with both servers running
- **THEN** the request succeeds without a CORS error

### Requirement: Environment variables are documented
A `.env.example` file at the repo root SHALL list every environment variable required by both apps, with placeholder values and a one-line comment describing each. Neither `.env` nor any file containing real secrets SHALL be committed to version control.

#### Scenario: New developer sets up environment
- **WHEN** a developer copies `.env.example` to `.env` and fills in the placeholders
- **THEN** both apps start successfully without missing-variable errors

#### Scenario: Secrets are gitignored
- **WHEN** a developer checks `git status` after creating `.env`
- **THEN** `.env` does not appear as a tracked or untracked file

### Requirement: Setup is documented in README
The root `README.md` SHALL contain step-by-step instructions to get both apps running locally, including virtual environment creation, dependency installation, and how to start each dev server.

#### Scenario: Developer follows README from scratch
- **WHEN** a developer follows only the README instructions on a clean machine
- **THEN** both apps are running locally within 10 minutes
