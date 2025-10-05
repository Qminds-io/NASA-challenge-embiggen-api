from __future__ import annotations

from collections import defaultdict, deque
from threading import Lock
from time import monotonic
from typing import Deque, Dict

from fastapi import HTTPException, Request, status

RATE_LIMIT_PER_MINUTE = 120
WINDOW_SECONDS = 60.0


class RateLimiter:
    def __init__(self, limit: int, window: float) -> None:
        self.limit = limit
        self.window = window
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def hit(self, key: str) -> None:
        now = monotonic()
        with self._lock:
            bucket = self._hits[key]
            while bucket and now - bucket[0] > self.window:
                bucket.popleft()
            if len(bucket) >= self.limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "status": "rate_limited",
                        "code": "too_many_requests",
                        "message": "Limite de solicitudes por minuto excedido.",
                    },
                )
            bucket.append(now)


rate_limiter = RateLimiter(limit=RATE_LIMIT_PER_MINUTE, window=WINDOW_SECONDS)


async def limit_db_requests(request: Request) -> None:
    client_host = request.client.host if request.client else "unknown"
    rate_limiter.hit(client_host)
