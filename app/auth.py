import secrets
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.config import settings

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key_header_val: str = Security(api_key_header)):
    if not api_key_header_val:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is missing. Please provide it in the X-API-Key header."
        )
    # Using constant-time comparison to prevent Timing Attacks on the API Key
    if not secrets.compare_digest(api_key_header_val, settings.API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key."
        )
    return api_key_header_val

