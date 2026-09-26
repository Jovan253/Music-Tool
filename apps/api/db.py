import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

_raw_url = os.environ.get("DATABASE_URL")
if not _raw_url:
    raise RuntimeError("DATABASE_URL environment variable is not set")


def _normalize_url(url: str) -> str:
    # Hosted Postgres providers hand out `postgres://`, which SQLAlchemy rejects
    # outright. Bare `postgresql://` is accepted but its default driver changed to
    # psycopg v3 in SQLAlchemy 2.1, so pin the driver explicitly rather than
    # inheriting whatever the installed version happens to default to.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


DATABASE_URL = _normalize_url(_raw_url)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
