import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

_url = os.environ.get("DATABASE_URL")
if not _url:
    raise RuntimeError("DATABASE_URL environment variable is not set")

engine = create_engine(_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
