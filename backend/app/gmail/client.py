import logging
from typing import Any
from googleapiclient.discovery import build, Resource
from app.gmail.auth import get_credentials

logger = logging.getLogger(__name__)


def get_gmail_client() -> Resource:
    """Initialize and return Google Gmail API client service resource."""
    creds = get_credentials()
    if not creds or not creds.valid:
        raise PermissionError(
            "Valid Google OAuth credentials not found. Please authenticate via /auth/login endpoint first."
        )
    
    try:
        service = build("gmail", "v1", credentials=creds)
        return service
    except Exception as e:
        logger.error(f"Failed to build Gmail service client: {e}")
        raise RuntimeError(f"Could not connect to Gmail API: {e}")
