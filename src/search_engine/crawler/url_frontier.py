from collections import deque

class UrlFrontier:
    def __init__(self) -> None:
        self._queue: deque[str] = deque()
        self._seen: set[str] = set()

    def add(self, url: str) -> bool:
        if url in self._seen:
            return False
        self._seen.add(url)
        self._queue.append(url)
        return True

    def has_next(self) -> bool:
        return len(self._queue) > 0

    def next(self) -> str:
        if not self._queue:
            raise IndexError("frontier is empty")
        return self._queue.popleft()

    def has_seen(self, url: str) -> bool:
        return url in self._seen

    @property
    def seen_count(self) -> int:
        return len(self._seen)

    def __len__(self) -> int:
        """Number of URLs currently QUEUED (not yet visited) -- not the
        total seen count."""
        return len(self._queue)