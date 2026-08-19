import base64
import logging
import re
from email.mime.text import MIMEText
from typing import List, Optional
from googleapiclient.discovery import Resource

from app.gmail.client import get_gmail_client
from app.models.email import EmailMessage, DraftReply, EmailThread
from app.core.retries import retry_on_transient_error

logger = logging.getLogger(__name__)


class GmailService:
    def __init__(self, client: Optional[Resource] = None):
        self._client = client

    @property
    def client(self) -> Resource:
        if self._client is None:
            self._client = get_gmail_client()
        return self._client

    @retry_on_transient_error
    def fetch_unread_emails(self, max_results: int = 10) -> List[EmailMessage]:

        """Fetch list of unread emails from user's inbox and parse into EmailMessage models."""
        try:
            results = (
                self.client.users()
                .messages()
                .list(userId="me", q="is:unread", maxResults=max_results)
                .execute()
            )
            messages_meta = results.get("messages", [])
            
            emails: List[EmailMessage] = []
            for msg_meta in messages_meta:
                try:
                    email_msg = self.get_email_by_id(msg_meta["id"])
                    emails.append(email_msg)
                except Exception as e:
                    logger.error(f"Error fetching detail for message {msg_meta.get('id')}: {e}")
                    
            logger.info(f"Successfully fetched {len(emails)} unread emails.")
            return emails
        except Exception as e:
            logger.error(f"Failed to fetch unread emails: {e}")
            raise RuntimeError(f"Gmail API error: {e}")

    @retry_on_transient_error
    def get_email_by_id(self, email_id: str) -> EmailMessage:
        """Fetch a specific email by ID and convert it to EmailMessage model."""
        try:
            raw_msg = (
                self.client.users()
                .messages()
                .get(userId="me", id=email_id, format="full")
                .execute()
            )
            return self._parse_raw_message(raw_msg)
        except Exception as e:
            logger.error(f"Failed to retrieve email {email_id}: {e}")
            raise RuntimeError(f"Could not fetch email {email_id}: {e}")

    @retry_on_transient_error
    def get_thread_by_id(self, thread_id: str) -> EmailThread:
        """Fetch all messages belonging to a specific Gmail thread."""
        try:
            raw_thread = (
                self.client.users()
                .threads()
                .get(userId="me", id=thread_id, format="full")
                .execute()
            )
            raw_messages = raw_thread.get("messages", [])
            parsed_messages = [self._parse_raw_message(msg) for msg in raw_messages]
            return EmailThread(thread_id=thread_id, messages=parsed_messages)
        except Exception as e:
            logger.warning(f"Could not fetch thread context for {thread_id}: {e}")
            return EmailThread(thread_id=thread_id, messages=[])

    @retry_on_transient_error
    def create_draft(self, draft_request: DraftReply) -> dict:

        """Create a Gmail Draft. NEVER automatically sends emails."""
        try:
            mime_msg = MIMEText(draft_request.body)
            mime_msg["to"] = draft_request.recipient
            mime_msg["subject"] = draft_request.subject

            # Encode as base64url string
            raw_encoded = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode("utf-8")
            
            body = {
                "message": {
                    "threadId": draft_request.thread_id,
                    "raw": raw_encoded,
                }
            }

            draft_result = (
                self.client.users()
                .drafts()
                .create(userId="me", body=body)
                .execute()
            )
            
            logger.info(
                f"Successfully created Gmail draft {draft_result.get('id')} for email {draft_request.email_id} (Thread: {draft_request.thread_id})"
            )
            return draft_result
        except Exception as e:
            logger.error(f"Failed to create draft for email {draft_request.email_id}: {e}")
            raise RuntimeError(f"Gmail draft creation failed: {e}")

    @retry_on_transient_error
    def send_message(self, draft_request: DraftReply) -> dict:
        """Directly send an email reply via Gmail API."""
        try:
            mime_msg = MIMEText(draft_request.body)
            mime_msg["to"] = draft_request.recipient
            mime_msg["subject"] = draft_request.subject

            # Encode as base64url string
            raw_encoded = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode("utf-8")

            body = {
                "threadId": draft_request.thread_id,
                "raw": raw_encoded,
            }

            send_result = (
                self.client.users()
                .messages()
                .send(userId="me", body=body)
                .execute()
            )

            logger.info(
                f"Successfully SENT email reply {send_result.get('id')} to {draft_request.recipient} for email {draft_request.email_id}"
            )
            return send_result
        except Exception as e:
            logger.error(f"Failed to send email reply for email {draft_request.email_id}: {e}")
            raise RuntimeError(f"Gmail send message failed: {e}")


    def _parse_raw_message(self, raw_msg: dict) -> EmailMessage:
        """Parse raw Gmail API response payload into typed EmailMessage model."""
        msg_id = raw_msg.get("id", "")
        thread_id = raw_msg.get("threadId", "")
        snippet = raw_msg.get("snippet", "")
        labels = raw_msg.get("labelIds", [])
        is_unread = "UNREAD" in labels

        payload = raw_msg.get("payload", {})
        headers = payload.get("headers", [])
        
        header_dict = {h.get("name", "").lower(): h.get("value", "") for h in headers}

        sender = header_dict.get("from", "Unknown Sender")
        recipient = header_dict.get("to", None)
        subject = header_dict.get("subject", "(No Subject)")
        date = header_dict.get("date", None)

        body_text = self._extract_body(payload)

        return EmailMessage(
            id=msg_id,
            thread_id=thread_id,
            sender=sender,
            recipient=recipient,
            subject=subject,
            body=body_text if body_text.strip() else snippet,
            snippet=snippet,
            date=date,
            is_unread=is_unread,
            labels=labels,
        )

    def _extract_body(self, payload: dict) -> str:
        """Recursively extract plain text or decoded HTML body from message payload."""
        body_data = ""
        
        # Check if direct body exists
        if "body" in payload and "data" in payload["body"]:
            body_data = payload["body"]["data"]
            decoded = self._decode_base64url(body_data)
            if payload.get("mimeType") == "text/html":
                return self._strip_html(decoded)
            return decoded

        # If payload has nested parts (multipart)
        if "parts" in payload:
            text_parts = []
            html_parts = []

            def _traverse(parts: list):
                for part in parts:
                    mime_type = part.get("mimeType", "")
                    if "parts" in part:
                        _traverse(part["parts"])
                    elif "body" in part and "data" in part["body"]:
                        part_data = self._decode_base64url(part["body"]["data"])
                        if mime_type == "text/plain":
                            text_parts.append(part_data)
                        elif mime_type == "text/html":
                            html_parts.append(part_data)

            _traverse(payload["parts"])

            if text_parts:
                return "\n".join(text_parts)
            if html_parts:
                return self._strip_html("\n".join(html_parts))

        return ""

    @staticmethod
    def _decode_base64url(data: str) -> str:
        """Decode base64url string safely."""
        try:
            decoded_bytes = base64.urlsafe_b64decode(data + "===")
            return decoded_bytes.decode("utf-8", errors="replace")
        except Exception:
            return ""

    @staticmethod
    def _strip_html(html_content: str) -> str:
        """Remove HTML tags for clean text parsing."""
        clean = re.sub(r"<style.*?>.*?</style>", "", html_content, flags=re.DOTALL)
        clean = re.sub(r"<script.*?>.*?</script>", "", clean, flags=re.DOTALL)
        clean = re.sub(r"<.*?>", " ", clean)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean
