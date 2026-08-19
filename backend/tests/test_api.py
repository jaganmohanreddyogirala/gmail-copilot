from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.email import EmailMessage, DraftReply

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "Gmail Copilot API"
    assert data["status"] == "running"


def test_auth_status_endpoint():
    response = client.get("/auth/status")
    assert response.status_code == 200
    data = response.json()
    assert "authenticated" in data


def test_process_email_endpoint(sample_email_message):
    payload = sample_email_message.model_dump()
    response = client.post("/emails/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["email"]["id"] == sample_email_message.id
    assert data["analysis"] is not None
    assert data["analysis"]["requires_reply"] is True
    assert data["draft"] is not None
    assert data["draft"]["email_id"] == sample_email_message.id


@patch("app.api.routes.GmailService")
def test_create_draft_endpoint(mock_gmail_service_class, sample_draft_reply):
    mock_service = MagicMock()
    mock_gmail_service_class.return_value = mock_service
    mock_service.create_draft.return_value = {"id": "gmail_draft_777"}

    payload = sample_draft_reply.model_dump()
    response = client.post("/emails/draft", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["gmail_draft_id"] == "gmail_draft_777"


def test_auth_login_pkce_store():
    from app.gmail.auth import _PKCE_STORE
    response = client.get("/auth/login", follow_redirects=False)
    assert response.status_code == 307
    location = response.headers["location"]
    assert "accounts.google.com" in location
    assert "code_challenge=" in location
    assert len(_PKCE_STORE) > 0

