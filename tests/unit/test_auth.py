import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from search_engine.api.auth import verify_api_key

def _protected_app() -> FastAPI:
    app = FastAPI()

    @app.get("/protected")
    def protected_route(api_key: str = Depends(verify_api_key)):
        return {"authenticated_as": api_key}

    return app

def test_valid_default_dev_key_is_accepted(monkeypatch):
    monkeypatch.delenv("SEARCH_ENGINE_API_KEYS", raising=False)
    client = TestClient(_protected_app())

    response = client.get("/protected", headers={"X-API-Key": "dev-key-change-me"})
    assert response.status_code == 200
    assert response.json()["authenticated_as"] == "dev-key-change-me"

def test_invalid_key_is_rejected(monkeypatch):
    monkeypatch.delenv("SEARCH_ENGINE_API_KEYS", raising=False)
    client = TestClient(_protected_app())

    response = client.get("/protected", headers={"X-API-Key": "totally-wrong-key"})
    assert response.status_code == 401

def test_missing_key_header_is_rejected():
    client = TestClient(_protected_app())
    response = client.get("/protected")
    assert response.status_code == 422

def test_custom_configured_keys_via_environment(monkeypatch):
    monkeypatch.setenv("SEARCH_ENGINE_API_KEYS", "key-one,key-two")
    client = TestClient(_protected_app())

    assert client.get("/protected", headers={"X-API-Key": "key-one"}).status_code == 200
    assert client.get("/protected", headers={"X-API-Key": "key-two"}).status_code == 200
    assert (
        client.get("/protected", headers={"X-API-Key": "dev-key-change-me"}).status_code == 401
    )

def test_keys_with_surrounding_whitespace_are_trimmed(monkeypatch):
    monkeypatch.setenv("SEARCH_ENGINE_API_KEYS", " key-one , key-two ")
    client = TestClient(_protected_app())
    assert client.get("/protected", headers={"X-API-Key": "key-one"}).status_code == 200