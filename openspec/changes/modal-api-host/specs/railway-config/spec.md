## REMOVED Requirements

### Requirement: railway.toml defines web and worker services
**Reason:** Railway is retired. It was the only paid component in the stack, and it was running four always-on services for an app with negligible traffic. The `worker` service in particular existed only to wait on a Modal call and move bytes — work that the Modal function now does itself.

**Migration:** `apps/api/railway.toml` is deleted. The API is served by the Modal app defined in `apps/api/modal_app.py` (see the `modal-api-host` capability). There is no longer a separate worker service to configure.

### Requirement: Migrations run on service start
**Reason:** `start.sh` ran `alembic upgrade head` before uvicorn on every Railway boot. Under Modal's scale-to-zero model there is no single startup event to hang migrations off, and running them per-container would race.

**Migration:** `apps/api/start.sh` is deleted. Migrations run through the dedicated `migrate()` Modal function, invoked explicitly as a deploy step.

### Requirement: Procfile fallback
**Reason:** The Procfile existed only as a fallback for Railway's build detection.

**Migration:** `apps/api/Procfile` is deleted.

### Requirement: Production env vars are documented for the Railway dashboard
**Reason:** The variable inventory is still needed, but its destination is no longer a Railway dashboard, and the set itself has changed: `REDIS_URL` and `RQ_REDIS_URL` are gone with the queue, and `DEMUCS_DEVICE` is only meaningful for the local development path.

**Migration:** `apps/api/.env.example` remains the inventory for local development, and the production set lives in a Modal Secret. `RUNBOOK.md` documents which variable comes from which dashboard.
