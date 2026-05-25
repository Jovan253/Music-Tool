from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, JSON
from db import Base


class JobModel(Base):
    __tablename__ = "jobs"

    job_id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False, default="")
    user_id = Column(String, nullable=True)
    stems = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    processing_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
