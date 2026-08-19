import pytest
from app.models.email import EmailMessage, DraftReply, EmailCategory, EmailPriority


@pytest.fixture
def sample_raw_gmail_message():
    return {
        "id": "msg_12345",
        "threadId": "thread_67890",
        "labelIds": ["UNREAD", "INBOX"],
        "snippet": "Can you review the PR for the auth service?",
        "payload": {
            "mimeType": "text/plain",
            "headers": [
                {"name": "From", "value": "Alice Developer <alice@engineering.com>"},
                {"name": "To", "value": "Engineer <engineer@company.com>"},
                {"name": "Subject", "value": "[URGENT] PR Review: Auth Service Fix"},
                {"name": "Date", "value": "Wed, 12 Aug 2026 10:00:00 +0000"},
            ],
            "body": {
                "data": "Q2FuIHlvdSByZXZpZXcgdGhlIFBSIGZvciB0aGUgYXV0aCBzZXJ2aWNlPwoKSHVnZSBibG9ja2VyIGZvciBvdXIgcmVsZWFzZS4="
            },
        },
    }


@pytest.fixture
def sample_email_message():
    return EmailMessage(
        id="msg_12345",
        thread_id="thread_67890",
        sender="Alice Developer <alice@engineering.com>",
        recipient="Engineer <engineer@company.com>",
        subject="[URGENT] PR Review: Auth Service Fix",
        body="Can you review the PR for the auth service?\n\nHuge blocker for our release.",
        snippet="Can you review the PR for the auth service?",
        date="Wed, 12 Aug 2026 10:00:00 +0000",
        is_unread=True,
        labels=["UNREAD", "INBOX"],
    )


@pytest.fixture
def sample_draft_reply():
    return DraftReply(
        email_id="msg_12345",
        thread_id="thread_67890",
        recipient="alice@engineering.com",
        subject="Re: [URGENT] PR Review: Auth Service Fix",
        body="Hi Alice,\n\nI will review the PR immediately.\n\nBest,\nEngineer",
        reasoning="Acknowledging urgent PR review request.",
    )
