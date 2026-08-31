from fastapi.testclient import TestClient

from search_engine.api.main import create_app
from search_engine.cli.main import SearchEngineCLI

_AUTH_HEADERS = {"X-API-Key": "dev-key-change-me"}

def _client_with_indexed_corpus(tmp_path) -> TestClient:
    (tmp_path / "doc1.txt").write_text("python programming search engine")
    (tmp_path / "doc2.txt").write_text("java programming enterprise")

    app = create_app(engine=SearchEngineCLI())
    client = TestClient(app)
    client.post("/index", params={"directory": str(tmp_path)}, headers=_AUTH_HEADERS)
    return client

def test_search_with_api_key_is_recorded_in_history(tmp_path):
    client = _client_with_indexed_corpus(tmp_path)
    client.get("/search", params={"q": "python"}, headers=_AUTH_HEADERS)

    response = client.get("/history", headers=_AUTH_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["total_queries"] == 1
    assert body["recent"][0]["query"] == "python"

def test_search_without_api_key_tracked_as_anonymous(tmp_path):
    client = _client_with_indexed_corpus(tmp_path)
    client.get("/search", params={"q": "python"})

    response = client.get("/history", headers=_AUTH_HEADERS)
    assert response.json()["total_queries"] == 0

def test_history_requires_auth(tmp_path):
    client = _client_with_indexed_corpus(tmp_path)
    response = client.get("/history")
    assert response.status_code == 422

def test_history_records_result_count(tmp_path):
    client = _client_with_indexed_corpus(tmp_path)
    client.get("/search", params={"q": "python"}, headers=_AUTH_HEADERS)
    client.get("/search", params={"q": "nonexistent"}, headers=_AUTH_HEADERS)

    response = client.get("/history", headers=_AUTH_HEADERS)
    recent = response.json()["recent"]
    result_counts = {r["query"]: r["result_count"] for r in recent}
    assert result_counts["python"] == 1
    assert result_counts["nonexistent"] == 0

def test_analytics_requires_auth(tmp_path):
    client = _client_with_indexed_corpus(tmp_path)
    response = client.get("/analytics")
    assert response.status_code == 422

def test_analytics_returns_aggregate_stats(tmp_path):
    client = _client_with_indexed_corpus(tmp_path)
    client.get("/search", params={"q": "python"}, headers=_AUTH_HEADERS)
    client.get("/search", params={"q": "python"}, headers=_AUTH_HEADERS)
    client.get("/search", params={"q": "java"}, headers=_AUTH_HEADERS)

    response = client.get("/analytics", headers=_AUTH_HEADERS)
    assert response.status_code == 200
    body = response.json()

    assert body["total_queries"] == 3
    assert body["top_queries"][0]["query"] == "python"
    assert body["top_queries"][0]["count"] == 2

def test_two_apps_have_isolated_history(tmp_path):
    (tmp_path / "doc.txt").write_text("shared content")

    app_a = create_app(engine=SearchEngineCLI())
    app_b = create_app(engine=SearchEngineCLI())
    client_a = TestClient(app_a)
    client_b = TestClient(app_b)

    client_a.get("/search", params={"q": "anything"}, headers=_AUTH_HEADERS)

    assert client_a.get("/history", headers=_AUTH_HEADERS).json()["total_queries"] == 1
    assert client_b.get("/history", headers=_AUTH_HEADERS).json()["total_queries"] == 0