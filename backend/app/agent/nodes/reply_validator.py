import logging
import re
from app.agent.state import AgentState

logger = logging.getLogger(__name__)


def reply_validator_node(state: AgentState) -> AgentState:
    """LangGraph node: Validate generated draft reply for security, formatting, and completeness."""
    draft = state.get("draft")
    email = state.get("email")

    if not draft:
        logger.info("Reply Validator: No draft present to validate.")
        state["validation_status"] = "SKIPPED"
        return state

    logger.info(f"Reply Validator: Validating draft for email {email.id if email else 'N/A'}")

    body = draft.body.lower()
    
    # Check for accidental credential leaks or placeholder tokens
    has_leak = any(token in body for token in ["ghp_", "sk-proj-", "bearer ", "password=", "secret="])
    has_unfilled_placeholders = bool(re.search(r"\[insert\b|\[your name\]|\[todo\]", body))

    if has_leak:
        logger.warning(f"Reply Validator FAILED: Sensitive token detected in draft body!")
        state["validation_status"] = "FAILED_SECURITY_LEAK"
        draft.body = "[REDACTED - DRAFT CONTAINED POTENTIAL SENSITIVE CREDENTIAL LEAK. RE-REVIEW REQUIRED]"
        draft.status = "pending_approval"
    elif has_unfilled_placeholders:
        logger.warning(f"Reply Validator WARN: Unfilled template placeholder detected.")
        state["validation_status"] = "PASSED_WITH_WARNING"
    else:
        state["validation_status"] = "PASSED"
        logger.info("Reply Validator PASSED cleanly.")

    state["draft"] = draft
    return state
