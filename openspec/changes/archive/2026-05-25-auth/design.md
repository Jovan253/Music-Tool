## Context

The app currently has no authentication. All job routes are public and jobs have no owner. Adding auth requires: a session layer on the frontend, JWT verification on the backend, and a `user_id` column on the `jobs` table. Supabase Auth is already available (the Supabase project is live for storage), so we use it rather than introducing a separate identity provider.

## Goals / Non-Goals

**Goals:**
- Email/password sign-up and login via Supabase Auth
- Frontend session management with auto-refresh
- Backend JWT verification on all job routes
- Jobs scoped to the authenticated user (create + read)

**Non-Goals:**
- Social / OAuth login (Google, GitHub, etc.)
- Email verification or password reset flows (Supabase handles these in the dashboard; no custom UI)
- Role-based access control
- Admin routes
- Backfilling `user_id` for existing jobs

## Decisions

### Use Supabase Auth JWT verification on the backend (no separate auth service)

Supabase issues standard JWTs signed with the project's JWT secret. The backend verifies the token locally using `python-jose` — no network call to Supabase on each request. The JWT secret is exposed as `SUPABASE_JWT_SECRET` in the backend env.

**Alternative considered**: Call Supabase's `GET /auth/v1/user` on every request to validate the token. Rejected: adds latency and a network dependency to every API call.

### Use `@supabase/supabase-js` on the frontend (no custom auth implementation)

The Supabase JS client handles session storage, token refresh, and expiry automatically. An `AuthContext` wraps the app and exposes the current user and session; all API calls read the token from context.

**Alternative considered**: Rolling a custom JWT storage layer. Rejected: unnecessary complexity; the Supabase client already handles edge cases (refresh, expiry, storage).

### `user_id` column: nullable with NOT NULL for new rows only

The migration adds `user_id VARCHAR` as nullable. No backfill — old rows keep `user_id = NULL` and become invisible after the change. New inserts enforce the value at the application layer (not a DB constraint yet), keeping the migration non-destructive and instantly reversible.

**Alternative considered**: Add NOT NULL with a sentinel backfill value. Rejected: sentinel values pollute the data model and the old jobs are useless anyway (they reference deleted local files).

### FastAPI dependency for auth (`get_current_user`)

A single `Depends(get_current_user)` injects the verified `user_id` string into any route that needs it. Routes that don't call this dependency remain public (e.g. `GET /health`).

## Risks / Trade-offs

- **JWT secret rotation** → All active sessions are invalidated. Mitigation: document that `SUPABASE_JWT_SECRET` must be treated as a long-lived secret; Supabase rotates it only on explicit request.
- **Old jobs become inaccessible** → No user_id means no owner match. Mitigation: documented as a known breaking change; old jobs were created during development and have no value.
- **Token expiry during long Demucs jobs** → The frontend token may expire before polling completes. Mitigation: the Supabase JS client auto-refreshes; the poll loop always reads the current session token, not a cached one.
- **`@supabase/supabase-js` bundle size** → Adds ~40 KB gzipped. Acceptable for this app.

## Migration Plan

1. Add `SUPABASE_JWT_SECRET` to `apps/api/.env` (get from Supabase → Settings → API → JWT Secret)
2. Add `SUPABASE_URL` and `SUPABASE_ANON_KEY` to `apps/web/.env` (anon key is public-safe)
3. Run Alembic migration to add `user_id` column
4. Deploy backend, then frontend — backend is backwards-compatible during the window (old requests get 401, which is correct)

**Rollback**: remove the `get_current_user` dependency from routes; the `user_id` column can stay (nullable, harmless).
