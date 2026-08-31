import time
from collections import deque

from fastapi import HTTPException, Request, status

class RateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: float = 60.0) -> None:
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = {}

    def is_allowed(self, client_id: str, current_time: float) -> bool:
        history = self._requests.setdefault(client_id, deque())

        cutoff = current_time - self._window_seconds
        while history and history[0] < cutoff:
            history.popleft()

        if len(history) >= self._max_requests:
            return False

        history.append(current_time)
        return True

    def request_count(self, client_id: str) -> int:
        return len(self._requests.get(client_id, []))

def rate_limit_dependency(limiter: RateLimiter):
    def dependency(request: Request) -> None:
        client_id = request.client.host if request.client else "unknown"
        if not limiter.is_allowed(client_id, time.monotonic()):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please slow down.",
            )

    return dependency