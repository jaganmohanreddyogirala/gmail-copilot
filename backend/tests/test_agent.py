import pytest
from app.agent.graph import email_agent_graph
from app.agent.nodes.classifier import classifier_node
from app.agent.nodes.reply_generator import reply_generator_node
from app.models.email import EmailMessage, EmailCategory, EmailPriority, AnalysisResult


def test_classifier_node_fallback(sample_email_message):
    initial_state = {"email": sample_email_message, "analysis": None, "draft": None, "error": None}
    res_state = classifier_node(initial_state)

    analysis = res_state.get("analysis")
    assert analysis is not None
    assert analysis.email_id == sample_email_message.id
    assert analysis.category in [EmailCategory.URGENT, EmailCategory.WORK]
    assert analysis.requires_reply is True


def test_reply_generator_node_fallback(sample_email_message):
    analysis = AnalysisResult(
        email_id=sample_email_message.id,
        category=EmailCategory.URGENT,
        priority=EmailPriority.P0,
        requires_reply=True,
        reasoning="Critical PR blocker",
        key_action_items=["Review PR"],
    )
    initial_state = {"email": sample_email_message, "analysis": analysis, "draft": None, "error": None}
    res_state = reply_generator_node(initial_state)

    draft = res_state.get("draft")
    assert draft is not None
    assert draft.email_id == sample_email_message.id
    assert draft.thread_id == sample_email_message.thread_id
    assert draft.recipient == sample_email_message.sender
    assert draft.subject.startswith("Re:")


def test_full_langgraph_workflow_urgent_email(sample_email_message):
    initial_state = {"email": sample_email_message, "analysis": None, "draft": None, "error": None}
    final_state = email_agent_graph.invoke(initial_state)

    assert final_state["analysis"] is not None
    assert final_state["analysis"].requires_reply is True
    assert final_state["draft"] is not None
    assert final_state["draft"].email_id == sample_email_message.id


def test_full_langgraph_workflow_notification_email():
    promo_email = EmailMessage(
        id="msg_promo",
        thread_id="thread_promo",
        sender="Marketing <newsletter@news.com>",
        recipient="me@company.com",
        subject="Weekly Tech Digest Newsletter (Unsubscribe)",
        body="Here is your weekly digest. Click here to unsubscribe.",
        snippet="Weekly digest...",
        is_unread=True,
    )
    initial_state = {"email": promo_email, "thread_context": None, "analysis": None, "mcp_context": None, "draft": None, "validation_status": None, "error": None}
    final_state = email_agent_graph.invoke(initial_state)

    assert final_state["analysis"] is not None
    assert final_state["analysis"].requires_reply is False
    assert final_state.get("draft") is None


def test_sensitive_credential_email_workflow():
    sensitive_email = EmailMessage(
        id="msg_sec",
        thread_id="thread_sec",
        sender="Security Team <security@company.com>",
        recipient="me@company.com",
        subject="[CRITICAL] Production Database API_KEY credentials leaked",
        body="Please rotate password and api_key immediately for prod database.",
        snippet="Security alert...",
        is_unread=True,
    )
    initial_state = {"email": sensitive_email, "thread_context": None, "analysis": None, "mcp_context": None, "draft": None, "validation_status": None, "error": None}
    final_state = email_agent_graph.invoke(initial_state)

    assert final_state["analysis"] is not None
    assert final_state["analysis"].requires_human_approval is True
    assert final_state["draft"] is not None
    assert final_state["draft"].status == "pending_approval"

