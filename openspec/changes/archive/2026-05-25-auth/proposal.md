## Why

Without auth, all jobs are global — any user can see every job, and there is no way to associate data with a person. Adding auth gates all job routes behind a valid session and scopes each job to its owner, making the app safe to share and enabling per-user features (history, settings, billing) in the future.

## What Changes

- Users can sign up and log in with email and password via Supabase Auth
- The frontend stores the Supabase session token and attaches it as a Bearer token on every API request
- All job-related API routes (`POST /upload`, `GET /jobs/{id}`, `GET /jobs/{id}/stems/{name}`, `POST /jobs/{id}/export`) require a valid JWT
- The `jobs` table gains a `user_id` column; job creation records the owner; reads are filtered to the authenticated user
- Unauthenticated requests receive `401 Unauthorized`
- **BREAKING**: existing jobs in the database have no `user_id` and will not be visible after migration (no backfill)

## Capabilities

### New Capabilities

- `user-auth`: Sign-up, login, logout, and session management via Supabase Auth; JWT verification on the backend

### Modified Capabilities

- `audio-upload`: `POST /upload` now requires authentication; `user_id` is written to the job record
- `job-persistence`: `jobs` table gains a `user_id` column; all queries filter by the authenticated user
- `stem-separation`: no requirement change — worker still reads `job_id` from the queue; no auth context needed in the worker
- `stem-mixer`: `GET /jobs/{id}/stems/{name}` now requires authentication
- `stem-export`: `POST /jobs/{id}/export` now requires authentication

## Impact

- **Frontend**: new auth screens (login, signup); `AuthContext` wrapping the app; token injected into all API calls; unauthenticated state redirects to login
- **Backend**: new `auth.py` dependency that verifies Supabase JWTs; all job routes receive `user_id` from the token; Alembic migration adds `user_id` column to `jobs`
- **Database**: Alembic migration — add nullable `user_id` column, then set NOT NULL for new rows (existing rows left NULL to avoid data loss)
- **Dependencies**: no new packages — Supabase JWT verification uses `python-jose` or Supabase's own JWT secret; frontend uses the existing `@supabase/supabase-js` client
