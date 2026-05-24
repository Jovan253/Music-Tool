import os
import redis
import rq
from fastapi import HTTPException

_queue: rq.Queue | None = None


def get_queue() -> rq.Queue:
    global _queue
    if _queue is None:
        url = os.environ.get("RQ_REDIS_URL", "redis://localhost:6379/0")
        try:
            conn = redis.Redis.from_url(url, socket_connect_timeout=2)
            conn.ping()
            _queue = rq.Queue("default", connection=conn)
        except redis.exceptions.ConnectionError as exc:
            raise HTTPException(status_code=503, detail="Queue service unavailable") from exc
    return _queue
