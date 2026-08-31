import os

from fastapi import Header, HTTPException, status

def _load_valid_api_keys() -> set[str]:
    raw = os.environ.get("SEARCH_ENGINE_API_KEYS", "dev-key-change-me")
    return {key.strip() for key in raw.split(",") if key.strip()}

def verify_api_key(x_api_key: str = Header(...)) -> str:
    valid_keys = _load_valid_api_keys()
    if x_api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return x_api_key