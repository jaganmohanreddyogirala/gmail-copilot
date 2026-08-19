from unittest.mock import MagicMock
import pytest
from app.gmail.service import GmailService
from app.models.email import EmailMessage, DraftReply


def test_parse_raw_message(sample_raw_gmail_message):
    service = GmailService(client=MagicMock())
    email = service._parse_raw_message(sample_raw_gmail_message)

    assert isinstance(email, EmailMessage)
    assert email.id == "msg_12345"
    assert email.thread_id == "thread_67890"
    assert email.sender == "Alice Developer <alice@engineering.com>"
    assert email.recipient == "Engineer <engineer@company.com>"
    assert email.subject == "[URGENT] PR Review: Auth Service Fix"
    assert email.is_unread is True
    assert "Can you review the PR" in email.body


def test_create_draft_payload(sample_draft_reply):
    mock_client = MagicMock()
    mock_drafts = MagicMock()
    mock_client.users.return_value.drafts.return_value = mock_drafts
    mock_drafts.create.return_value.execute.return_value = {"id": "draft_99999"}

    service = GmailService(client=mock_client)
    res = service.create_draft(sample_draft_reply)

    assert res["id"] == "draft_99999"
    mock_drafts.create.assert_called_once()
    
    # Ensure threadId was passed in payload body
    call_args = mock_drafts.create.call_args[1]
    assert call_args["userId"] == "me"
    assert call_args["body"]["message"]["threadId"] == "thread_67890"
    assert "raw" in call_args["body"]["message"]


def test_decode_base64url():
    data = "SGVsbG8gV29ybGQ="
    decoded = GmailService._decode_base64url(data)
    assert decoded == "Hello World"


def test_strip_html():
    html = "<div><p>Hello <b>World</b></p><style>body {color:red;}</style></div>"
    text = GmailService._strip_html(html)
    assert text == "Hello World"
