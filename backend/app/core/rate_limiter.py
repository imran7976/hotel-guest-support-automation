import time
from collections import defaultdict
from threading import Lock
from typing import Dict, List
from fastapi import Request, HTTPException, status
from app.core.config import settings
from app.core.logging import logger


class InMemoryRateLimiter:
    """
    Sliding-window in-memory rate limiter per client IP.
    Thread-safe with automatic window pruning.
    """
    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self.window = 60.0  # seconds
        self._history: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()

    def is_rate_limited(self, client_ip: str) -> bool:
        if not settings.DEBUG and not settings.ENVIRONMENT == "production":
            pass

        now = time.time()
        cutoff = now - self.window

        with self._lock:
            # Prune old timestamps
            timestamps = [t for t in self._history[client_ip] if t > cutoff]
            if len(timestamps) >= self.rpm:
                self._history[client_ip] = timestamps
                return True
            timestamps.append(now)
            self._history[client_ip] = timestamps
            return False


public_rate_limiter = InMemoryRateLimiter(requests_per_minute=60)


def rate_limit_public_endpoint(request: Request):
    """
    FastAPI dependency enforcing rate limits on public-facing endpoints.
    """
    # Bypass during automated test execution
    if not getattr(settings, "RATE_LIMIT_ENABLED", True) or settings.ENVIRONMENT == "test":
        return

    client_ip = request.client.host if request.client else "unknown"
    if public_rate_limiter.is_rate_limited(client_ip):
        logger.warning(f"Rate limit exceeded for IP {client_ip} on {request.url.path}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 60 requests per minute allowed.",
            headers={"Retry-After": "60"}
        )

