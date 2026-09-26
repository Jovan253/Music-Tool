import os
import tempfile
from pathlib import Path

# Must be set before importing main: db.py and storage/supabase_storage.py both
# raise at import time when their vars are missing.
#
# SQLite rather than Postgres so service-layer tests can hit a real database in CI
# with nothing to provision — every column type in models/job.py is generic. Note
# this is an assignment, not setdefault: a developer's .env points DATABASE_URL at
# Neon, and tests must never write to it.
_TEST_DB = Path(tempfile.gettempdir()) / "tracksplit_test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB}"
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
os.environ.setdefault("SUPABASE_ANON_KEY", "test-anon-key")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def app():
    import main

    return main.app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def db():
    from db import Base, engine
    import models.job  # noqa: F401 — registers JobModel on Base.metadata

    Base.metadata.create_all(engine)
    try:
        yield
    finally:
        Base.metadata.drop_all(engine)
