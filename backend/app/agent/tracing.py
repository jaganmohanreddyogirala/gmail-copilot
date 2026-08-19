import logging
import time
import uuid
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.db import ExecutionTraceRecord
from app.models.email import ExecutionTrace
from app.agent.state import AgentState
from app.config import settings


logger = logging.getLogger(__name__)


async def record_execution_trace(
    db: AsyncSession,
    state: AgentState,
    processing_time_ms: float,
) -> ExecutionTrace:
    """Record structured Agent Execution Trace in PostgreSQL/SQLite for complete observability."""
    email = state["email"]
    analysis = state.get("analysis")
    draft = state.get("draft")
    validation_status = state.get("validation_status") or "PASSED"

    intent = analysis.intent.value if (analysis and hasattr(analysis.intent, "value")) else (getattr(analysis, "intent", "Action Required"))
    priority = analysis.priority.value if (analysis and hasattr(analysis.priority, "value")) else (getattr(analysis, "priority", "P1"))
    risk = analysis.risk_level.value if (analysis and hasattr(analysis.risk_level, "value")) else (getattr(analysis, "risk_level", "Low"))

    decision = "IGNORED"
    if draft:
        if draft.status == "pending_approval":
            decision = "NEEDS_HUMAN_APPROVAL"
        elif draft.status == "created":
            decision = "DRAFT_CREATED"
        else:
            decision = "DRAFT_GENERATED"
    elif analysis and analysis.requires_human_approval:
        decision = "NEEDS_HUMAN_APPROVAL"

    trace_id = f"trace_{uuid.uuid4().hex[:12]}"
    
    confidence = getattr(analysis, "confidence", 0.90) if analysis else 0.90

    agent_state_summary = {
        "email_id": email.id,
        "subject": email.subject,
        "sender": email.sender,
        "confidence": confidence,
        "has_mcp_context": state.get("mcp_context") is not None,
        "has_user_style": state.get("user_style") is not None,
        "validation_status": validation_status,
        "node_latencies": state.get("node_latencies") or {},
        "error": state.get("error"),
    }


    record = ExecutionTraceRecord(
        id=trace_id,
        email_id=email.id,
        thread_id=email.thread_id,
        intent=str(intent),
        priority=str(priority),
        risk=str(risk),
        decision=decision,
        agent_state=agent_state_summary,
        model_used=settings.LLM_MODEL,
        processing_time_ms=f"{processing_time_ms:.1f}",
        draft_created=draft is not None,
        human_approved=True if draft and draft.status == "created" else (False if draft and draft.status == "pending_approval" else None),
        validation_result=validation_status,
    )

    try:
        db.add(record)
        await db.commit()
        logger.info(f"Recorded Execution Trace {trace_id} for Email {email.id} (Decision: {decision})")
    except Exception as e:
        logger.error(f"Failed to record trace to database: {e}")
        await db.rollback()

    return ExecutionTrace(
        id=trace_id,
        email_id=email.id,
        thread_id=email.thread_id,
        intent=str(intent),
        priority=str(priority),
        risk=str(risk),
        decision=decision,
        confidence=confidence,
        agent_state=agent_state_summary,
        model_used=settings.LLM_MODEL,
        processing_time_ms=round(processing_time_ms, 1),
        draft_created=draft is not None,
        human_approved=record.human_approved,
        validation_result=validation_status,
    )



async def get_recent_traces(db: AsyncSession, limit: int = 20) -> List[ExecutionTraceRecord]:
    """Retrieve recent agent execution traces for dashboard visualization."""
    stmt = select(ExecutionTraceRecord).order_by(ExecutionTraceRecord.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
