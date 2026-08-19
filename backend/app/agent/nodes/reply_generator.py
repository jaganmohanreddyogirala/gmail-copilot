import logging
from langchain_core.prompts import ChatPromptTemplate
from app.agent.state import AgentState
from app.agent.nodes.classifier import get_llm
from app.models.email import DraftReply

logger = logging.getLogger(__name__)

REPLY_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert AI engineering copilot drafting replies on behalf of a software engineer.\n"
        "Draft a concise, professional, direct, and helpful reply to the email below.\n"
        "STRICTLY ADHERE TO THE FOLLOWING RETRIEVED USER STYLE MEMORY RULES:\n"
        "{user_style_rules}\n\n"
        "Format output as structured DraftReply.",
    ),
    (
        "human",
        "Original Email Sender: {sender}\n"
        "Original Subject: {subject}\n"
        "Original Body:\n{body}\n\n"
        "External MCP Context (Calendar / GitHub):\n{mcp_context}\n\n"
        "Analysis Context:\nCategory: {category}\nPriority: {priority}\nReasoning: {reasoning}\nAction Items: {action_items}\n",
    ),
])



def reply_generator_node(state: AgentState) -> AgentState:
    """LangGraph node: Generate concise engineering draft reply for emails requiring action."""
    email = state["email"]
    analysis = state.get("analysis")

    logger.info(f"Generating draft reply for email {email.id} (Sender: {email.sender})")

    # Format reply subject
    subject = email.subject if email.subject.lower().startswith("re:") else f"Re: {email.subject}"
    
    # Extract clean email address for recipient if possible
    recipient = email.sender

    # Extract user style and MCP context
    user_style = state.get("user_style")
    style_rules_str = "\n".join([f"- {r}" for r in getattr(user_style, "custom_rules", ["Be concise."])]) if user_style else "- Be concise and professional."
    
    mcp_ctx = state.get("mcp_context")
    mcp_str = "None"
    if mcp_ctx:
        mcp_items = (mcp_ctx.calendar_events or []) + (mcp_ctx.github_context or [])
        if mcp_items:
            mcp_str = "\n".join(mcp_items)

    # Check offline_mode for deterministic evaluation
    if state.get("offline_mode"):
        status = "pending_approval" if (analysis and getattr(analysis, "requires_human_approval", False)) else "created"
        fallback_body = (
            f"Hi,\n\n"
            f"Thank you for reaching out regarding '{email.subject}'. "
            f"I have received your email and will review the details shortly.\n\n"
            f"Best regards,\nEngineering Team"
        )
        draft = DraftReply(
            email_id=email.id,
            thread_id=email.thread_id,
            recipient=recipient,
            subject=subject,
            body=fallback_body,
            reasoning="Generated deterministic offline draft reply matching user style memory.",
            status=status,
        )
        state["draft"] = draft
        return state

    llm = get_llm()

    if llm and analysis:
        try:
            structured_llm = llm.with_structured_output(DraftReply)
            prompt = REPLY_PROMPT.format_messages(
                sender=email.sender,
                subject=email.subject,
                body=email.body,
                user_style_rules=style_rules_str,
                mcp_context=mcp_str,
                category=analysis.category,
                priority=analysis.priority,
                reasoning=analysis.reasoning,
                action_items=", ".join(analysis.key_action_items),
            )

            draft: DraftReply = structured_llm.invoke(prompt)
            # Ensure metadata consistency
            draft.email_id = email.id
            draft.thread_id = email.thread_id
            draft.recipient = recipient
            if not draft.subject:
                draft.subject = subject
            if analysis and getattr(analysis, "requires_human_approval", False):
                draft.status = "pending_approval"
            state["draft"] = draft
            return state
        except Exception as e:
            logger.error(f"LLM draft reply generation error for email {email.id}: {e}")

    # Fallback draft generation
    logger.warning("Using fallback draft generator.")
    fallback_body = (
        f"Hi,\n\n"
        f"Thank you for reaching out regarding '{email.subject}'. "
        f"I have received your email and will review the details shortly.\n\n"
        f"Best regards,\nEngineering Team"
    )
    
    status = "pending_approval" if (analysis and getattr(analysis, "requires_human_approval", False)) else "created"
    
    draft = DraftReply(
        email_id=email.id,
        thread_id=email.thread_id,
        recipient=recipient,
        subject=subject,
        body=fallback_body,
        reasoning="Generated fallback draft template pending detailed engineer review.",
        status=status,
    )
    state["draft"] = draft
    return state

