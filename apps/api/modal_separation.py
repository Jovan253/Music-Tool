from pathlib import Path

import modal

API_DIR = Path(__file__).parent
REMOTE_DIR = "/root/api"

# Generous because a cold container pulls Demucs weights before it starts work.
# Actual separation on a T4 is ~25s for a typical track.
SEPARATION_TIMEOUT_S = 900

secret = modal.Secret.from_name(
    "music-tool",
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
    .apt_install("ffmpeg")
    # The local-separation extra is where torch/torchaudio/demucs are pinned, so
    # the image and a local CPU install can never drift apart.
    .pip_install_from_pyproject(
        str(API_DIR / "pyproject.toml"), optional_dependencies=["local-separation"]
    )
    .add_local_dir(
        API_DIR,
        remote_path=REMOTE_DIR,
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

app = modal.App("music-tool-separation")


@app.function(
    gpu="T4",
    image=image,
    secrets=[secret],
    timeout=SEPARATION_TIMEOUT_S,
    retries=2,
)
def separate_job(job_id: str) -> None:
    import os
    import sys

    if REMOTE_DIR not in sys.path:
        sys.path.insert(0, REMOTE_DIR)

    # Assert the GPU rather than letting auto-detection quietly fall back to CPU,
    # which would burn the whole timeout instead of failing.
    os.environ["DEMUCS_DEVICE"] = "cuda"

    from workers.separation import run_separation

    run_separation(job_id)
