import logging

from fastapi.testclient import TestClient

from search_engine.api.main import create_app
from search_engine.cli.main import SearchEngineCLI

def test_requests_are_logged(caplog):
    app = create_app(engine=SearchEngineCLI())
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="search_engine.observability.middleware"):
        response = client.get("/stats")

    assert response.status_code == 200
    assert any("GET" in record.message and "/stats" in record.message for record in caplog.records)

def test_log_includes_status_code(caplog):
    app = create_app(engine=SearchEngineCLI())
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="search_engine.observability.middleware"):
        client.get("/search")

    assert any("422" in record.message for record in caplog.records)

def test_app_still_functions_normally_with_middleware_attached(tmp_path):
    (tmp_path / "doc.txt").write_text("python programming")
    app = create_app(engine=SearchEngineCLI())
    client = TestClient(app)

    index_response = client.post(
        "/index", params={"directory": str(tmp_path)}, headers={"X-API-Key": "dev-key-change-me"}
    )
    assert index_response.status_code == 200

    search_response = client.get("/search", params={"q": "python"})
    assert search_response.status_code == 200
    assert search_response.json()["count"] == 1