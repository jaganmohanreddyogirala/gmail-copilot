import logging
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery
from app.config import settings

logger = logging.getLogger(__name__)

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
API_KEY_QUERY = APIKeyQuery(name="api_key", auto_error=False)


async def verify_api_key(
    api_key_header: str = Security(API_KEY_HEADER),
    api_key_query: str = Security(API_KEY_QUERY),
):
    """Verify incoming API Key header or query parameter if auth is enabled."""
    if not settings.ENABLE_AUTH:
        return True

    key = api_key_header or api_key_query
    if key == settings.API_SECRET_KEY:
        return True

    logger.warning("Unauthorized API access attempt with invalid key.")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key header (X-API-Key).",
    )
