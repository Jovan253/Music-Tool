import logging
import os
from pathlib import Path
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

_env_path = Path(__file__).parent / ".env"
load_dotenv(_env_path)
log.info("Loaded .env from %s", _env_path)
log.info("SUPABASE_URL set: %s", bool(os.environ.get("SUPABASE_URL")))
log.info("SUPABASE_KEY set: %s", bool(os.environ.get("SUPABASE_SERVICE_ROLE_KEY")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.upload import router as upload_router
from routes.jobs import router as jobs_router
from routes.stems import router as stems_router
from routes.export import router as export_router
from routes.demo import router as demo_router

# No startup stale-job sweep: under Modal's scale-to-zero model containers start
# and stop constantly, so a sweep would fire on every cold start and re-run jobs
# that are legitimately in flight. Modal function retries cover that instead.
app = FastAPI(title="TrackSplit API")

_cors_origins = [
    o.strip()
    for o in os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(jobs_router)
app.include_router(stems_router)
app.include_router(export_router)
app.include_router(demo_router)


@app.get("/health")
def health():
    return {"status": "ok"}
