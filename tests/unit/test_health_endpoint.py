from fastapi.testclient import TestClient

from search_engine.api.main import create_app
from search_engine.cli.main import SearchEngineCLI

def test_health_returns_ok():
    app = create_app(engine=SearchEngineCLI())
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_health_does_not_require_auth():
    app = create_app(engine=SearchEngineCLI())
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200

def test_health_works_even_with_no_documents_indexed():
    app = create_app(engine=SearchEngineCLI())
    client = TestClient(app)

    assert client.get("/stats").json()["document_count"] == 0
    assert client.get("/health").status_code == 200