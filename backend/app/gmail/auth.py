import os
import json
import logging
from typing import Optional, Tuple
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from app.config import settings

logger = logging.getLogger(__name__)


from app.config import Settings


def get_client_config() -> dict:
    """Construct Google OAuth client config dictionary from environment variables or file."""
    current_settings = Settings()
    if current_settings.GOOGLE_CLIENT_ID and current_settings.GOOGLE_CLIENT_SECRET:
        return {
            "web": {
                "client_id": current_settings.GOOGLE_CLIENT_ID,
                "client_secret": current_settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [current_settings.GOOGLE_REDIRECT_URI],
            }
        }
    
    if os.path.exists(settings.GMAIL_CREDENTIALS_PATH):
        with open(settings.GMAIL_CREDENTIALS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
            
    raise ValueError(
        "Google OAuth credentials missing! Provide GOOGLE_CLIENT_ID & GOOGLE_CLIENT_SECRET in .env or credentials.json"
    )


def get_credentials() -> Optional[Credentials]:
    """Retrieve stored OAuth2 credentials or refresh them if expired with retry logic."""
    creds = None
    token_path = settings.GMAIL_TOKEN_PATH

    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, settings.GMAIL_SCOPES)
        except Exception as e:
            logger.warning(f"Failed to load credentials from {token_path}: {e}")
            creds = None

    if creds and (creds.expired or not creds.valid) and creds.refresh_token:
        try:
            logger.info("Refreshing expired Google OAuth access token...")
            req = Request()
            creds.refresh(req)
            save_credentials(creds)
            logger.info("Successfully refreshed and saved updated Google OAuth access token.")
        except Exception as e:
            logger.error(f"Failed to refresh OAuth token (credentials may be revoked or expired): {e}")
            creds = None

    return creds if (creds and creds.valid) else None



def save_credentials(creds: Credentials) -> None:
    """Save user credentials to token file."""
    with open(settings.GMAIL_TOKEN_PATH, "w", encoding="utf-8") as token_file:
        token_file.write(creds.to_json())
    logger.info(f"Saved OAuth credentials to {settings.GMAIL_TOKEN_PATH}")


_PKCE_STORE: dict[str, str] = {}


def create_flow(state: Optional[str] = None) -> Flow:
    """Create OAuth Flow object."""
    client_config = get_client_config()
    flow = Flow.from_client_config(
        client_config=client_config,
        scopes=settings.GMAIL_SCOPES,
        state=state,
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    return flow


def get_authorization_url() -> Tuple[str, str]:
    """Generate authorization URL and state for user OAuth login."""
    flow = create_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    if hasattr(flow, "code_verifier") and flow.code_verifier:
        _PKCE_STORE[state] = flow.code_verifier
        logger.info(f"Stored PKCE code_verifier for state: {state[:8]}...")
    return authorization_url, state


def fetch_token_from_code(code: str, state: Optional[str] = None) -> Credentials:
    """Exchange OAuth authorization code for credentials and store them."""
    import requests
    current_settings = Settings()
    client_config = get_client_config()["web"]
    
    token_url = client_config.get("token_uri", "https://oauth2.googleapis.com/token")
    payload = {
        "code": code,
        "client_id": client_config["client_id"],
        "client_secret": client_config["client_secret"],
        "redirect_uri": client_config["redirect_uris"][0],
        "grant_type": "authorization_code",
    }
    
    if state and state in _PKCE_STORE:
        code_verifier = _PKCE_STORE.pop(state)
        payload["code_verifier"] = code_verifier
        logger.info("Attached PKCE code_verifier to token exchange payload.")
    
    response = requests.post(token_url, data=payload)
    if response.status_code != 200:
        logger.error(f"Token exchange error: {response.status_code} - {response.text}")
        raise ValueError(f"Token exchange failed: {response.text}")
        
    token_data = response.json()
    
    existing_creds = get_credentials()
    refresh_token = token_data.get("refresh_token")
    if not refresh_token and existing_creds and existing_creds.refresh_token:
        refresh_token = existing_creds.refresh_token
    
    creds = Credentials(
        token=token_data.get("access_token"),
        refresh_token=refresh_token,
        token_uri=token_url,
        client_id=client_config["client_id"],
        client_secret=client_config["client_secret"],
        scopes=current_settings.GMAIL_SCOPES,
    )
    
    save_credentials(creds)
    return creds

