from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from search_engine.api.rate_limiter import RateLimiter, rate_limit_dependency

def test_allows_requests_under_the_limit():
    limiter = RateLimiter(max_requests=3, window_seconds=60.0)

    assert limiter.is_allowed("client-a", current_time=100.0) is True
    assert limiter.is_allowed("client-a", current_time=100.1) is True
    assert limiter.is_allowed("client-a", current_time=100.2) is True

def test_blocks_requests_over_the_limit():
    limiter = RateLimiter(max_requests=2, window_seconds=60.0)

    assert limiter.is_allowed("client-a", current_time=100.0) is True
    assert limiter.is_allowed("client-a", current_time=100.1) is True
    assert limiter.is_allowed("client-a", current_time=100.2) is False

def test_old_requests_outside_window_are_pruned_allowing_new_ones():
    limiter = RateLimiter(max_requests=2, window_seconds=10.0)

    limiter.is_allowed("client-a", current_time=100.0)
    limiter.is_allowed("client-a", current_time=100.1)
    assert limiter.is_allowed("client-a", current_time=100.2) is False

    assert limiter.is_allowed("client-a", current_time=115.0) is True

def test_different_clients_are_tracked_independently():
    limiter = RateLimiter(max_requests=1, window_seconds=60.0)

    assert limiter.is_allowed("client-a", current_time=100.0) is True
    assert limiter.is_allowed("client-a", current_time=100.1) is False
    assert limiter.is_allowed("client-b", current_time=100.1) is True

def test_request_count_reflects_current_window():
    limiter = RateLimiter(max_requests=5, window_seconds=60.0)
    limiter.is_allowed("client-a", current_time=100.0)
    limiter.is_allowed("client-a", current_time=100.1)

    assert limiter.request_count("client-a") == 2
    assert limiter.request_count("never-seen-client") == 0

def test_rate_limit_dependency_integration_with_fastapi():
    limiter = RateLimiter(max_requests=2, window_seconds=60.0)
    app = FastAPI()

    @app.get("/limited", dependencies=[Depends(rate_limit_dependency(limiter))])
    def limited_route():
        return {"ok": True}

    client = TestClient(app)

    assert client.get("/limited").status_code == 200
    assert client.get("/limited").status_code == 200
    assert client.get("/limited").status_code == 429