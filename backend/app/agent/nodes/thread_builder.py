import logging
from app.agent.state import AgentState
from app.gmail.service import GmailService

logger = logging.getLogger(__name__)


def thread_builder_node(state: AgentState) -> AgentState:
    """LangGraph node: Fetch and attach full conversation thread history context."""
    email = state["email"]
    if state.get("offline_mode"):
        state["thread_context"] = None
        return state

    logger.info(f"Thread Context Builder: Fetching history for thread_id {email.thread_id}")

    try:
        service = GmailService()
        thread_context = service.get_thread_by_id(email.thread_id)
        state["thread_context"] = thread_context
        logger.info(f"Attached {len(thread_context.messages)} messages to thread context.")
    except Exception as e:
        logger.warning(f"Thread context lookup skipped: {e}")
        state["thread_context"] = None

    return state

