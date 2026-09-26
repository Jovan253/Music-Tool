import os

# Must be set before importing main: db.py and storage/supabase_storage.py both
# raise at import time when their vars are missing. setdefault (not assignment)
# keeps a real local .env authoritative, and load_dotenv does not override.
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
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
