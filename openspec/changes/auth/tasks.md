## 1. Environment Setup (manual)

- [x] 1.1 In Supabase dashboard → Settings → API, copy the **JWT Secret** and add `SUPABASE_JWT_SECRET=<value>` to `apps/api/.env` and `.env.example`
- [x] 1.2 Copy the **anon (public) key** from Supabase → Settings → API and add `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` to `apps/web/.env` (create it from `.env.example` if needed)
- [x] 1.3 Add `python-jose[cryptography]>=3.3` to `apps/api/pyproject.toml` and install into venv

## 2. Backend — JWT Verification

- [x] 2.1 Create `apps/api/auth.py` — read `SUPABASE_JWT_SECRET` at import (raise `RuntimeError` if missing); implement `get_current_user(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> str` that decodes the JWT with `python-jose`, validates `exp`, and returns the `sub` claim as `user_id`; raise `HTTPException(401)` on any failure

## 3. Database Migration

- [x] 3.1 Add `user_id` column to `JobModel` in `apps/api/models/job.py` — `Column(String, nullable=True)`
- [x] 3.2 Run `alembic revision --autogenerate -m "add user_id to jobs"` and `alembic upgrade head`

## 4. Backend — Protect Routes

- [x] 4.1 Update `apps/api/services/jobs.py` — add `user_id` parameter to `create_job`; add `user_id` filter to `get_job` (returns `None` if `user_id` doesn't match); add `get_jobs_for_user(user_id: str)` if needed
- [x] 4.2 Update `apps/api/routes/upload.py` — add `user_id: str = Depends(get_current_user)`; pass `user_id` to `create_job`
- [x] 4.3 Update `apps/api/routes/jobs.py` — add `user_id: str = Depends(get_current_user)`; pass `user_id` to `get_job`
- [x] 4.4 Update `apps/api/routes/stems.py` — add `user_id: str = Depends(get_current_user)`; pass `user_id` to `get_job`
- [x] 4.5 Update `apps/api/routes/export.py` — add `user_id: str = Depends(get_current_user)`; pass `user_id` to `get_job`

## 5. Frontend — Supabase Auth Client

- [x] 5.1 Install `@supabase/supabase-js` — `npm install @supabase/supabase-js` in `apps/web`
- [x] 5.2 Create `apps/web/src/lib/supabase.ts` — initialise and export the Supabase client using `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`
- [x] 5.3 Create `apps/web/src/features/auth/AuthContext.tsx` — provide `user`, `session`, `signIn(email, password)`, `signUp(email, password)`, `signOut()` via React context; subscribe to `onAuthStateChange` for session refresh

## 6. Frontend — Auth UI

- [x] 6.1 Create `apps/web/src/features/auth/LoginPage.tsx` — email/password form with toggle to sign-up mode; calls `signIn` or `signUp` from context; shows error messages on failure
- [x] 6.2 Update `apps/web/src/App.tsx` — wrap with `AuthProvider`; if no session, render `<LoginPage />`; if session, render the existing upload/mixer flow

## 7. Frontend — Attach Token to API Calls

- [x] 7.1 Update `apps/web/src/lib/api.ts` — export a `setAuthToken(token: string | null)` setter; update `uploadFile` and `request` to include `Authorization: Bearer <token>` header when a token is set
- [x] 7.2 Update `apps/web/src/features/auth/AuthContext.tsx` — call `setAuthToken(session.access_token)` on sign-in / session restore and `setAuthToken(null)` on sign-out

## 8. Verification

- [ ] 8.1 Unauthenticated: confirm `POST /upload` returns `401` without a token
- [ ] 8.2 Sign up a new user — confirm the account appears in Supabase → Authentication → Users
- [ ] 8.3 Log in, upload a file — confirm it processes end-to-end and stems appear
- [ ] 8.4 Log in as a different user — confirm the first user's jobs return `404`
- [ ] 8.5 Reload the page while logged in — confirm the session is restored without a new login prompt
