import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging
from app.config import settings
from app.gmail.auth import get_credentials, get_authorization_url
from app.gmail.service import GmailService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("--- Stage 1 Gmail API & Auth Verification ---")
    logger.info(f"App Environment: {settings.APP_ENV}")
    logger.info(f"Token Path: {settings.GMAIL_TOKEN_PATH}")

    creds = get_credentials()
    if not creds:
        logger.info("No valid OAuth credentials found locally.")
        logger.info("Generating OAuth authorization URL...")
        try:
            url, state = get_authorization_url()
            logger.info(f"Please visit this URL to authenticate:\n{url}")
            logger.info("After authenticating, exchange the code via the API callback endpoint.")
        except Exception as e:
            logger.error(f"Could not generate authorization URL: {e}")
            logger.info("Make sure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are configured in backend/.env")
        return

    logger.info("OAuth credentials found and valid!")
    try:
        service = GmailService()
        logger.info("Fetching unread emails...")
        emails = service.fetch_unread_emails(max_results=5)
        logger.info(f"Retrieved {len(emails)} unread email(s):")
        for i, email in enumerate(emails, 1):
            print(f"\n[{i}] Subject: {email.subject}")
            print(f"    From: {email.sender}")
            print(f"    Date: {email.date}")
            print(f"    Snippet: {email.snippet}")
            print(f"    Body snippet: {email.body[:150]}...")
    except Exception as e:
        logger.error(f"Failed to fetch emails: {e}")


if __name__ == "__main__":
    main()
