This change was implemented in May 2026 and then undone on 2026-09-26 by
`modal-api-host`.

Railway was the only paid component in the stack and was running four always-on
services — web, worker, Postgres, Redis — for an app with negligible traffic. Its
Free plan grants $1/month of credit, nowhere near enough; Hobby is $5/month with
an included credit that four services would likely exceed.

Everything this change added is gone: `railway.toml`, `Procfile` and `start.sh`
are deleted, and the `railway-config` capability was never promoted into
`openspec/specs/` because it was removed before it could be. `start.sh`'s
`alembic upgrade head` step survives as `modal_app.py::migrate`, now an explicit
one-shot rather than something that ran on every boot.

The tasks below are all ticked and were genuinely done at the time. Read them as
history, not as a description of the current system. Current hosting is specified
in `openspec/specs/modal-api-host/spec.md`.
