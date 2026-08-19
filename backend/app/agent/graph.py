import logging
import time
from typing import Callable
from langgraph.graph import StateGraph, START, END
from app.agent.state import AgentState
from app.agent.nodes.thread_builder import thread_builder_node
from app.agent.nodes.classifier import classifier_node
from app.agent.nodes.human_approval import human_approval_node
from app.agent.nodes.style_memory import style_memory_node
from app.agent.nodes.reply_generator import reply_generator_node
from app.agent.nodes.reply_validator import reply_validator_node
from app.agent.tools.mcp_tools import fetch_mcp_context
from app.models.email import RiskLevel

logger = logging.getLogger(__name__)


def profile_node(node_name: str, fn: Callable[[AgentState], AgentState]) -> Callable[[AgentState], AgentState]:
    """Higher-order function recording start/end time and duration_ms for node-level latency profiling."""
    def wrapper(state: AgentState) -> AgentState:
        t0 = time.time()
        if not state.get("start_time_ms"):
            state["start_time_ms"] = t0 * 1000

        result_state = fn(state)

        t1 = time.time()
        duration_ms = round((t1 - t0) * 1000, 2)

        if "node_latencies" not in result_state or result_state["node_latencies"] is None:
            result_state["node_latencies"] = {}
        result_state["node_latencies"][node_name] = duration_ms

        logger.info(f"Node '{node_name}' completed in {duration_ms:.1f} ms")
        return result_state

    return wrapper


def mcp_context_node(state: AgentState) -> AgentState:
    """LangGraph Node: Fetch external MCP context (Calendar + GitHub) for incoming email."""
    email = state["email"]
    logger.info(f"MCP Context Builder: Querying external tools for email {email.id}")
    mcp_ctx = fetch_mcp_context(email.subject, email.body)
    state["mcp_context"] = mcp_ctx
    return state


def route_classification(state: AgentState) -> str:
    """Confidence-aware edge router:
    - High Risk / Security Rule OR Confidence < 0.60 -> human_approval
    - Confidence >= 0.85 -> style_memory (automated reply generation)
    - 0.60 <= Confidence < 0.85 -> style_memory (verification path)
    - Reply Not Required -> END
    """
    analysis = state.get("analysis")
    if not analysis or not analysis.requires_reply:
        logger.info(f"Email {state['email'].id} ignored / reply not required. Routing to END.")
        return END

    confidence = getattr(analysis, "confidence", 0.90)
    risk_lvl = getattr(analysis, "risk_level", RiskLevel.LOW)
    req_approval = getattr(analysis, "requires_human_approval", False)

    # Safety rules ALWAYS take precedence over confidence
    if req_approval or risk_lvl == RiskLevel.HIGH or risk_lvl == "High - Requires Human Review" or confidence < 0.60:
        logger.info(
            f"Email {state['email'].id} routed to human_approval (Risk: {risk_lvl}, Approval: {req_approval}, Confidence: {confidence:.2f})"
        )
        return "human_approval"

    logger.info(f"Email {state['email'].id} routed to style_memory (Confidence: {confidence:.2f})")
    return "style_memory"


# Build LangGraph StateGraph
workflow = StateGraph(AgentState)

# Add profiled processing nodes
workflow.add_node("thread_builder", profile_node("thread_builder", thread_builder_node))
workflow.add_node("mcp_context", profile_node("mcp_context", mcp_context_node))
workflow.add_node("classify", profile_node("classify", classifier_node))
workflow.add_node("human_approval", profile_node("human_approval", human_approval_node))
workflow.add_node("style_memory", profile_node("style_memory", style_memory_node))
workflow.add_node("generate_reply", profile_node("generate_reply", reply_generator_node))
workflow.add_node("validate_reply", profile_node("validate_reply", reply_validator_node))

# Set workflow entrypoint
workflow.add_edge(START, "thread_builder")
workflow.add_edge("thread_builder", "mcp_context")
workflow.add_edge("mcp_context", "classify")

# Add conditional confidence-aware routing edge from classifier
workflow.add_conditional_edges(
    "classify",
    route_classification,
    {
        "human_approval": "human_approval",
        "style_memory": "style_memory",
        END: END,
    },
)

# Connect workflow branches
workflow.add_edge("human_approval", "style_memory")
workflow.add_edge("style_memory", "generate_reply")
workflow.add_edge("generate_reply", "validate_reply")
workflow.add_edge("validate_reply", END)

# Compile LangGraph app
email_agent_graph = workflow.compile()
