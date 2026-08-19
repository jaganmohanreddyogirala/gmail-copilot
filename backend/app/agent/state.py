from typing import TypedDict, Optional, Dict
from app.models.email import EmailMessage, EmailThread, AnalysisResult, DraftReply, MCPContext, UserStyleMemory



class AgentState(TypedDict):
    """LangGraph state schema for email processing workflow."""
    email: EmailMessage
    thread_context: Optional[EmailThread]
    analysis: Optional[AnalysisResult]
    mcp_context: Optional[MCPContext]
    user_style: Optional[UserStyleMemory]
    draft: Optional[DraftReply]
    validation_status: Optional[str]
    start_time_ms: Optional[float]
    node_latencies: Optional[Dict[str, float]]
    node_retry_counts: Optional[Dict[str, int]]
    offline_mode: Optional[bool]
    error: Optional[str]




