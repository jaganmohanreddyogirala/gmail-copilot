import logging
from app.agent.state import AgentState

logger = logging.getLogger(__name__)


def human_approval_node(state: AgentState) -> AgentState:
    """LangGraph node: Pause and place draft into human review queue for high-risk or sensitive emails."""
    email = state["email"]
    analysis = state.get("analysis")
    draft = state.get("draft")

    logger.info(f"Human Approval Node: Processing email {email.id} (Risk: {getattr(analysis, 'risk_level', 'Unknown')})")

    if draft:
        draft.status = "pending_approval"
        draft.reasoning = f"Draft held for engineer review due to {getattr(analysis, 'risk_reasoning', 'high risk evaluation')}."
        state["draft"] = draft

    return state
