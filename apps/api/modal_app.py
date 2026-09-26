from pathlib import Path

import modal

API_DIR = Path(__file__).parent
REMOTE_DIR = "/root/api"

# required_keys makes a missing variable fail when the secret resolves at deploy
# time, instead of at container import once traffic is already arriving.
secret = modal.Secret.from_name(
    "tracksplit",
    required_keys=[
        "DATABASE_URL",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_ANON_KEY",
        "SECRET_KEY",
        "CORS_ORIGINS",
    ],
)

image = (
    modal.Image.debian_slim(python_version="3.11")
    # pydub shells out to ffmpeg for the export mixdown and the MP3 transcode.
    .apt_install("ffmpeg")
    .pip_install_from_pyproject(str(API_DIR / "pyproject.toml"))
    .add_local_dir(
        API_DIR,
        remote_path=REMOTE_DIR,
        # .env would bake real credentials into an image layer, and .venv would
        # add gigabytes. add_local_dir rather than add_local_python_source
        # because the latter drops non-.py files that alembic needs.
        ignore=[
            ".env",
            ".env.local",
            ".venv",
            ".venv/**",
            "tests",
            "tests/**",
            "__pycache__",
            "**/__pycache__/**",
            "**/*.pyc",
        ],
    )
)

app = modal.App("tracksplit-api")


def _add_api_to_path() -> None:
    import sys

    if REMOTE_DIR not in sys.path:
        sys.path.insert(0, REMOTE_DIR)


@app.function(image=image, secrets=[secret], timeout=120)
@modal.asgi_app()
def fastapi_app():
    _add_api_to_path()
    from main import app as web_app

    return web_app


@app.function(
    image=image,
    secrets=[secret],
    schedule=modal.Period(days=1),
    timeout=900,
)
def retention_sweep() -> str:
    _add_api_to_path()
    from workers.retention import expire_old_jobs

    # Also the Supabase keep-alive: the free tier pauses a project after 7 days of
    # inactivity and only a dashboard click revives it. This sweep queries the
    # database and touches storage daily, so it keeps the project awake. If it ever
    # stops running, that pause becomes a second, quieter failure.
    return expire_old_jobs().summary()


@app.function(image=image, secrets=[secret], timeout=600)
def migrate() -> None:
    _add_api_to_path()
    from alembic import command
    from alembic.config import Config

    # script_location in alembic.ini is %(here)s-relative, so pointing Config at
    # the copied ini resolves the migration scripts without depending on cwd.
    command.upgrade(Config(f"{REMOTE_DIR}/alembic.ini"), "head")
