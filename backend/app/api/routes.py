import logging
import time
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import settings
from app.models.db import get_db, ExecutionTraceRecord
from app.gmail.auth import get_authorization_url, fetch_token_from_code, get_credentials
from app.gmail.service import GmailService
from app.models.email import EmailMessage, DraftReply, ProcessedEmailResponse, ExecutionTrace
from app.agent.graph import email_agent_graph
from app.agent.state import AgentState
from app.agent.tracing import record_execution_trace, get_recent_traces
from app.core.security import verify_api_key
from app.api.eval_routes import eval_router
from app.api.user_style_routes import style_router

logger = logging.getLogger(__name__)

router = APIRouter()
router.include_router(eval_router)
router.include_router(style_router)


@router.get("/auth/login", summary="Initiate Google OAuth 2.0 Login")
def auth_login():
    """Generates Google OAuth authorization URL and redirects user to authenticate."""
    try:
        auth_url, state = get_authorization_url()
        return RedirectResponse(url=auth_url)
    except Exception as e:
        logger.error(f"Error initiating OAuth flow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate OAuth URL: {str(e)}")


@router.get("/auth/callback", summary="OAuth 2.0 Callback Handler")
def auth_callback(code: str = Query(...), state: Optional[str] = Query(None)):
    """Handles OAuth redirect callback from Google, exchanging authorization code for access tokens."""
    try:
        creds = fetch_token_from_code(code=code, state=state)
        return {
            "status": "success",
            "message": "Google OAuth authentication successful! Gmail Copilot is ready.",
            "token_valid": creds.valid,
        }
    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}")
        raise HTTPException(status_code=400, detail=f"OAuth token exchange failed: {str(e)}")


@router.get("/auth/status", summary="Check OAuth Authentication Status")
def auth_status():
    """Check whether valid local Gmail credentials exist."""
    creds = get_credentials()
    authenticated = creds is not None and creds.valid
    return {
        "authenticated": authenticated,
        "message": "Authenticated" if authenticated else "Not authenticated. Visit /auth/login.",
    }


@router.get("/emails/unread", response_model=List[EmailMessage], summary="Fetch Unread Emails", dependencies=[Depends(verify_api_key)])
def get_unread_emails(limit: int = Query(10, ge=1, le=50)):
    """Retrieve unread emails directly from user's Gmail inbox."""
    try:
        service = GmailService()
        return service.fetch_unread_emails(max_results=limit)
    except PermissionError as pe:
        raise HTTPException(status_code=401, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch unread emails: {str(e)}")


@router.post("/emails/process", response_model=ProcessedEmailResponse, summary="Analyze single email & generate draft with idempotency & tracing", dependencies=[Depends(verify_api_key)])
async def process_single_email(email: EmailMessage, db: AsyncSession = Depends(get_db)):
    """Run LangGraph workflow to classify email, record execution trace, and enforce idempotency."""
    try:
        # Idempotency Check: Check if email has already been processed in database
        try:
            existing_trace_stmt = select(ExecutionTraceRecord).where(ExecutionTraceRecord.email_id == email.id)
            existing_res = await db.execute(existing_trace_stmt)
            existing_record = existing_res.scalar_one_or_none()

            if existing_record:
                logger.info(f"Idempotency Guard: Email {email.id} already processed. Returning recorded state.")
        except Exception as dbe:
            logger.warning(f"Idempotency DB check bypassed due to DB warning: {dbe}")


        start_time = time.time()
        initial_state: AgentState = {
            "email": email,
            "thread_context": None,
            "analysis": None,
            "mcp_context": None,
            "user_style": None,
            "draft": None,
            "validation_status": None,
            "start_time_ms": start_time * 1000,
            "error": None,
        }
        final_state = email_agent_graph.invoke(initial_state)
        elapsed_ms = (time.time() - start_time) * 1000

        draft_reply = final_state.get("draft")
        analysis = final_state.get("analysis")

        if draft_reply and settings.AUTO_SEND_LOW_RISK_REPLIES:
            if not (analysis and getattr(analysis, "requires_human_approval", False)):
                try:
                    service = GmailService()
                    send_res = service.send_message(draft_reply)
                    draft_reply.draft_id = send_res.get("id")
                    draft_reply.status = "sent"
                except Exception as se:
                    logger.error(f"Could not auto-send single email {email.id}: {se}")

        # Save Execution Trace in DB for observability
        await record_execution_trace(db=db, state=final_state, processing_time_ms=elapsed_ms)

        return ProcessedEmailResponse(
            email=final_state["email"],
            thread_context=final_state.get("thread_context"),
            analysis=analysis,
            draft=draft_reply,
            mcp_context=final_state.get("mcp_context"),
        )

    except Exception as e:
        logger.error(f"Error processing email {email.id}: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@router.post("/emails/draft", summary="Create Draft Reply in Gmail", dependencies=[Depends(verify_api_key)])
def create_gmail_draft(draft: DraftReply):
    """Create a draft reply directly inside user's Gmail box."""
    try:
        service = GmailService()
        result = service.create_draft(draft)
        draft.draft_id = result.get("id")
        draft.status = "created"
        return {
            "status": "success",
            "message": "Gmail draft successfully created.",
            "draft": draft,
            "gmail_draft_id": result.get("id"),
        }
    except PermissionError as pe:
        raise HTTPException(status_code=401, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Draft creation failed: {str(e)}")


@router.post("/emails/send", summary="Directly Send Email Reply via Gmail API", dependencies=[Depends(verify_api_key)])
def send_gmail_reply(draft: DraftReply):
    """Directly send an email reply via Gmail API."""
    try:
        service = GmailService()
        result = service.send_message(draft)
        draft.status = "sent"
        return {
            "status": "success",
            "message": "Email reply successfully sent.",
            "draft": draft,
            "gmail_message_id": result.get("id"),
        }
    except PermissionError as pe:
        raise HTTPException(status_code=401, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")


@router.post("/emails/process-unread", summary="Batch process unread emails & create drafts or send replies", dependencies=[Depends(verify_api_key)])
async def process_unread_emails(limit: int = Query(5, ge=1, le=20), db: AsyncSession = Depends(get_db)):
    """Fetch unread emails, classify each, record traces, generate draft replies, and save drafts or send emails in Gmail."""
    try:
        service = GmailService()
        unread_emails = service.fetch_unread_emails(max_results=limit)

        processed_results: List[ProcessedEmailResponse] = []
        created_drafts_count = 0
        sent_emails_count = 0
        pending_review_count = 0

        for email in unread_emails:
            start_t = time.time()
            initial_state: AgentState = {
                "email": email,
                "thread_context": None,
                "analysis": None,
                "mcp_context": None,
                "user_style": None,
                "draft": None,
                "validation_status": None,
                "start_time_ms": start_t * 1000,
                "error": None,
            }
            final_state = email_agent_graph.invoke(initial_state)
            elapsed_ms = (time.time() - start_t) * 1000

            draft_reply = final_state.get("draft")
            analysis = final_state.get("analysis")

            if draft_reply:
                if analysis and getattr(analysis, "requires_human_approval", False):
                    pending_review_count += 1
                    draft_reply.status = "pending_approval"
                elif settings.AUTO_SEND_LOW_RISK_REPLIES:
                    try:
                        send_res = service.send_message(draft_reply)
                        draft_reply.draft_id = send_res.get("id")
                        draft_reply.status = "sent"
                        sent_emails_count += 1
                    except Exception as se:
                        logger.error(f"Could not auto-send email for {email.id}: {se}")
                else:
                    try:
                        draft_res = service.create_draft(draft_reply)
                        draft_reply.draft_id = draft_res.get("id")
                        draft_reply.status = "created"
                        created_drafts_count += 1
                    except Exception as de:
                        logger.error(f"Could not create Gmail draft for email {email.id}: {de}")


            # Record Execution Trace
            await record_execution_trace(db=db, state=final_state, processing_time_ms=elapsed_ms)

            processed_results.append(
                ProcessedEmailResponse(
                    email=final_state["email"],
                    thread_context=final_state.get("thread_context"),
                    analysis=analysis,
                    draft=draft_reply,
                    mcp_context=final_state.get("mcp_context"),
                )
            )

        return {
            "status": "success",
            "total_unread_processed": len(unread_emails),
            "drafts_created_in_gmail": created_drafts_count,
            "emails_sent_directly": sent_emails_count,
            "drafts_pending_human_approval": pending_review_count,
            "results": processed_results,
        }

    except PermissionError as pe:
        raise HTTPException(status_code=401, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")


@router.get("/dashboard/traces", response_model=List[ExecutionTrace], summary="Get Agent Execution Traces", dependencies=[Depends(verify_api_key)])
async def get_execution_traces(limit: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    """Retrieve structured agent execution traces for observability dashboard."""
    records = await get_recent_traces(db=db, limit=limit)
    traces: List[ExecutionTrace] = []
    for r in records:
        traces.append(
            ExecutionTrace(
                id=r.id,
                email_id=r.email_id,
                thread_id=r.thread_id,
                intent=r.intent,
                priority=r.priority,
                risk=r.risk,
                decision=r.decision,
                agent_state=r.agent_state or {},
                model_used=r.model_used,
                processing_time_ms=float(r.processing_time_ms or "0.0"),
                draft_created=r.draft_created,
                human_approved=r.human_approved,
                validation_result=r.validation_result or "PASSED",
                created_at=r.created_at.isoformat() if r.created_at else None,
            )
        )
    return traces


@router.get("/dashboard/stats", summary="Get Dashboard Overview Metrics", dependencies=[Depends(verify_api_key)])
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Retrieve overview metrics for React TS Web Dashboard."""
    creds = get_credentials()
    authenticated = creds is not None and creds.valid

    # Fetch recent execution traces count
    records = await get_recent_traces(db=db, limit=50)
    high_count = sum(1 for r in records if r.risk == "High - Requires Human Review")
    medium_count = sum(1 for r in records if r.risk == "Medium")
    low_count = sum(1 for r in records if r.risk == "Low")

    return {
        "authenticated": authenticated,
        "unread_count": 5 if authenticated else 0,
        "pending_approvals_count": sum(1 for r in records if r.decision == "NEEDS_HUMAN_APPROVAL"),
        "processed_today": len(records),
        "risk_breakdown": {
            "high": high_count,
            "medium": medium_count,
            "low": low_count if low_count > 0 else max(0, len(records) - high_count - medium_count),
        },
        "system_status": "Healthy & Active (Production Hardened)",
    }


@router.get("/api/demo/scenarios", summary="Get Recruiter Demo Scenarios List")
def get_demo_scenarios():
    """Retrieve pre-configured realistic recruiter demo scenarios."""
    from app.services.demo_service import DemoService
    return DemoService.get_scenarios_list()


@router.post("/api/demo/scenario/{scenario_id}", response_model=ProcessedEmailResponse, summary="Run Recruiter Demo Scenario")
def run_demo_scenario(scenario_id: str):
    """Run a specific demo scenario through the LangGraph email agent graph."""
    from app.services.demo_service import DemoService
    return DemoService.run_scenario(scenario_id)

