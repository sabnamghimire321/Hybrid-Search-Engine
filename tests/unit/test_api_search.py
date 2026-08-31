from fastapi.testclient import TestClient

from search_engine.api.main import create_app
from search_engine.cli.main import SearchEngineCLI

_AUTH_HEADERS = {"X-API-Key": "dev-key-change-me"}

def _make_corpus(tmp_path):
    (tmp_path / "python_guide.txt").write_text(
        "Python is a great programming language for search engines."
    )
    (tmp_path / "java_notes.txt").write_text(
        "Java is also a popular programming language used in enterprises."
    )
    return tmp_path

def _client_with_fresh_engine() -> TestClient:
    app = create_app(engine=SearchEngineCLI())
    return TestClient(app)

def test_index_endpoint_indexes_a_directory(tmp_path):
    corpus = _make_corpus(tmp_path)
    client = _client_with_fresh_engine()

    response = client.post(
        "/index", params={"directory": str(corpus)}, headers=_AUTH_HEADERS
    )

    assert response.status_code == 200
    body = response.json()
    assert body["indexed"] == 2
    assert body["document_count"] == 2

def test_index_endpoint_missing_directory_returns_404():
    client = _client_with_fresh_engine()
    response = client.post(
        "/index", params={"directory": "/definitely/not/a/real/path"}, headers=_AUTH_HEADERS
    )
    assert response.status_code == 404

def test_index_endpoint_without_api_key_is_rejected(tmp_path):
    corpus = _make_corpus(tmp_path)
    client = _client_with_fresh_engine()

    response = client.post("/index", params={"directory": str(corpus)})
    assert response.status_code == 422

def test_index_endpoint_with_wrong_api_key_is_rejected(tmp_path):
    corpus = _make_corpus(tmp_path)
    client = _client_with_fresh_engine()

    response = client.post(
        "/index", params={"directory": str(corpus)}, headers={"X-API-Key": "wrong-key"}
    )
    assert response.status_code == 401

def test_search_endpoint_returns_matching_documents(tmp_path):
    corpus = _make_corpus(tmp_path)
    client = _client_with_fresh_engine()
    client.post("/index", params={"directory": str(corpus)}, headers=_AUTH_HEADERS)

    response = client.get("/search", params={"q": "programming language"})

    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "programming language"
    assert body["count"] == 2
    titles = {r["title"] for r in body["results"]}
    assert titles == {"python_guide", "java_notes"}

def test_search_endpoint_no_results(tmp_path):
    corpus = _make_corpus(tmp_path)
    client = _client_with_fresh_engine()
    client.post("/index", params={"directory": str(corpus)}, headers=_AUTH_HEADERS)

    response = client.get("/search", params={"q": "nonexistentword"})

    assert response.status_code == 200
    assert response.json()["count"] == 0
    assert response.json()["results"] == []

def test_search_endpoint_requires_query_param():
    client = _client_with_fresh_engine()
    response = client.get("/search")
    assert response.status_code == 422

def test_search_endpoint_rejects_empty_query():
    client = _client_with_fresh_engine()
    response = client.get("/search", params={"q": ""})
    assert response.status_code == 422

def test_search_endpoint_does_not_require_api_key():
    client = _client_with_fresh_engine()
    response = client.get("/search", params={"q": "anything"})
    assert response.status_code == 200

def test_stats_endpoint_reflects_indexed_corpus(tmp_path):
    corpus = _make_corpus(tmp_path)
    client = _client_with_fresh_engine()
    client.post("/index", params={"directory": str(corpus)}, headers=_AUTH_HEADERS)

    response = client.get("/stats")
    body = response.json()
    assert body["document_count"] == 2
    assert body["vocabulary_size"] > 0

def test_two_clients_have_isolated_engines(tmp_path):
    corpus = _make_corpus(tmp_path)
    client_a = _client_with_fresh_engine()
    client_b = _client_with_fresh_engine()

    client_a.post("/index", params={"directory": str(corpus)}, headers=_AUTH_HEADERS)

    assert client_a.get("/stats").json()["document_count"] == 2
    assert client_b.get("/stats").json()["document_count"] == 0