import time

class CrawlScheduler:
    def __init__(self, default_delay: float = 1.0) -> None:
        self._default_delay = default_delay
        self._last_fetch_time: dict[str, float] = {}
        self._domain_delay: dict[str, float] = {}

    def set_domain_delay(self, domain: str, delay: float) -> None:
        self._domain_delay[domain] = delay

    def delay_for(self, domain: str) -> float:
        return self._domain_delay.get(domain, self._default_delay)

    def time_until_allowed(self, domain: str, current_time: float) -> float:
        last_time = self._last_fetch_time.get(domain)
        if last_time is None:
            return 0.0

        elapsed = current_time - last_time
        required = self.delay_for(domain)
        return max(0.0, required - elapsed)

    def record_fetch(self, domain: str, current_time: float) -> None:
        self._last_fetch_time[domain] = current_time

    def wait_if_needed(self, domain: str) -> float:
        now = time.monotonic()
        wait_time = self.time_until_allowed(domain, now)
        if wait_time > 0:
            time.sleep(wait_time)
            now = time.monotonic()
        self.record_fetch(domain, now)
        return wait_time