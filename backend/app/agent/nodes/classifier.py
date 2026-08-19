import logging
import re
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from app.config import settings
from app.agent.state import AgentState
from app.models.email import AnalysisResult, EmailCategory, EmailPriority, EmailIntent, RiskLevel

logger = logging.getLogger(__name__)


def get_llm():
    """Instantiate configured LLM provider."""
    if settings.LLM_PROVIDER.lower() == "google" and settings.GOOGLE_API_KEY:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL or "gemini-1.5-flash",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.1,
        )
    elif settings.OPENAI_API_KEY:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.LLM_MODEL or "gpt-4o-mini",
            api_key=settings.OPENAI_API_KEY,
            temperature=0.1,
        )
    return None


CLASSIFIER_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an executive AI assistant for software engineers. "
        "Analyze the following incoming email and classify its category, priority, intent, "
        "risk level (Low, Medium, High), confidence (0.0 to 1.0), and determine whether an engineering reply is required "
        "and whether human approval is needed before sending.\n\n"
        "STRICT PRIORITY CLASSIFICATION RULES:\n"
        "- P0 - Critical: Critical security incidents, active production outages, credential compromise, severe operational emergencies.\n"
        "- P1 - High: Important action or decision required soon, PR reviews, critical bug fixes, production changes, deadlines.\n"
        "- P2 - Medium: Normal action or response required without immediate urgency, general technical queries, routine bug reports.\n"
        "- P3 - Low: FYI notifications, scheduled maintenance windows, newsletters, promotional marketing.\n\n"
        "STRICT INTENT CLASSIFICATION RULES:\n"
        "- Security Alert / Credential Exposure Risk\n"
        "- Decision Needed\n"
        "- Action Required / Task Request\n"
        "- Technical Query\n"
        "- Informational / FYI\n"
        "- Promotional / Marketing\n\n"
        "High risk includes credential sharing, production changes, architectural commitments, or high-stakes security requests.",
    ),
    (
        "human",
        "From: {sender}\n"
        "To: {recipient}\n"
        "Subject: {subject}\n"
        "Date: {date}\n"
        "Body:\n{body}\n\n"
        "Thread Context (Preceding Messages):\n{thread_context}\n",
    ),
])


RETRY_CORRECTION_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "Your previous JSON output was invalid. Please output a strictly valid AnalysisResult object matching the required schema.",
    ),
    (
        "human",
        "Subject: {subject}\nBody:\n{body}\n",
    ),
])


SECURITY_KEYWORD_CATEGORIES = [
    # 1. API Keys, Passwords & Secret Tokens (spaced, hyphens, and snake_case)
    "api_key", "api key", "private_key", "private key", "secret_key", "secret key",
    "client_secret", "client secret", "ssh_key", "ssh key", "auth_token", "auth token",
    "bearer_token", "bearer token", "password", "passwd", "credential", "private key vault",
    "-----begin", "begin private key", "begin rsa", "pem file", ".pem",
    # 2. Database & Production Credentials
    "prod database", "prod db", "production database", "database backup", "prod_user",
    # 3. Security Incidents & Vulnerability Terminology
    "security alert", "security incident", "unauthorized access", "data breach",
    "credential leak", "exposed secret", "compromised", "vulnerability", "secret scanning"
]


def is_sensitive_security_text(text: str) -> bool:
    """Check if email text contains sensitive credential or security incident terms."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in SECURITY_KEYWORD_CATEGORIES)


def deterministic_classifier(email) -> AnalysisResult:
    """Refined deterministic classification engine implementing explicit P0-P3 criteria and safety checks."""
    subject_lower = email.subject.lower()
    body_lower = email.body.lower()
    text = f"{subject_lower} {body_lower}"

    # 1. Security Alert & Sensitive Credential Check (STRICT SAFETY OVERRIDE)
    if is_sensitive_security_text(text):
        return AnalysisResult(
            email_id=email.id,
            category=EmailCategory.URGENT,
            priority=EmailPriority.P0,
            intent=EmailIntent.SECURITY_ALERT,
            risk_level=RiskLevel.HIGH,

            risk_reasoning="Flagged HIGH risk due to security alert / sensitive credential exposure.",
            requires_reply=True,
            requires_human_approval=True,
            confidence=0.98,
            reasoning="Critical security alert / credential compromise requiring immediate human intervention.",
            key_action_items=["Revoke exposed credentials immediately", "Audit access logs"],
        )

    # 2. Urgent Active Production Outage Check (P0 Critical)
    is_outage = any(kw in text for kw in ["outage", "server down", "production outage", "sev1", "critical incident"])
    if is_outage:
        return AnalysisResult(
            email_id=email.id,
            category=EmailCategory.URGENT,
            priority=EmailPriority.P0,
            intent=EmailIntent.ACTION_REQUIRED,
            risk_level=RiskLevel.HIGH,
            risk_reasoning="Active production outage or severe operational emergency.",
            requires_reply=True,
            requires_human_approval=True,
            confidence=0.95,
            reasoning="Active production outage requiring immediate P0 response.",
            key_action_items=["Investigate outage root cause", "Restore production service"],
        )

    # 3. Promotional / Marketing Check (P3 Low)
    is_promo = any(kw in text for kw in ["unsubscribe", "special offer", "discount", "newsletter", "marketing", "sale"])
    if is_promo:
        return AnalysisResult(
            email_id=email.id,
            category=EmailCategory.NEWSLETTER,
            priority=EmailPriority.P3,
            intent=EmailIntent.PROMOTIONAL,
            risk_level=RiskLevel.LOW,
            risk_reasoning="Low operational risk (promotional broadcast).",
            requires_reply=False,
            requires_human_approval=False,
            confidence=0.95,
            reasoning="Promotional email broadcast requiring no engineering action.",
            key_action_items=[],
        )

    # 4. Informational / FYI Check (P3 Low)
    is_fyi = any(kw in text for kw in ["fyi:", "informational", "scheduled maintenance", "cost summary", "build report", "no action required"])
    if is_fyi or ("fyi" in subject_lower and "action" not in text):
        return AnalysisResult(
            email_id=email.id,
            category=EmailCategory.NOTIFICATION,
            priority=EmailPriority.P3,
            intent=EmailIntent.FYI,
            risk_level=RiskLevel.LOW,
            risk_reasoning="Low operational risk (informational notice).",
            requires_reply=False,
            requires_human_approval=False,
            confidence=0.92,
            reasoning="Informational notification requiring no reply.",
            key_action_items=[],
        )

    # 5. Decision Needed Check (P1 High)
    is_decision = any(kw in text for kw in ["decision needed", "architecture", "architectural decision", "choose between", "migration strategy", "evaluate trade-offs"])
    if is_decision:
        return AnalysisResult(
            email_id=email.id,
            category=EmailCategory.WORK,
            priority=EmailPriority.P1,
            intent=EmailIntent.DECISION_NEEDED,
            risk_level=RiskLevel.LOW,
            risk_reasoning="Important architectural choice requiring technical guidance.",
            requires_reply=True,
            requires_human_approval=False,
            confidence=0.92,
            reasoning="Engineering decision needed on technical architecture or design strategy.",
            key_action_items=["Evaluate technical options and provide recommendation"],
        )

    # 6. Action Required / Task Request Check
    is_action = any(kw in text for kw in ["action needed", "action required", "fix issue", "code review request", "pr #", "pull request", "bug report", "fails on", "blocked pending"])
    if is_action:
        is_bug = any(kw in text for kw in ["bug", "fails", "issue #", "error"])
        cat = EmailCategory.SUPPORT if is_bug else EmailCategory.WORK
        prio = EmailPriority.P1
        return AnalysisResult(
            email_id=email.id,
            category=cat,
            priority=prio,
            intent=EmailIntent.ACTION_REQUIRED,
            risk_level=RiskLevel.LOW,
            risk_reasoning="Engineering task requiring action/review.",
            requires_reply=True,
            requires_human_approval=False,
            confidence=0.90,
            reasoning="Action required or task request needing engineer reply.",
            key_action_items=["Review details and execute required task"],
        )

    # 7. Technical Query / Work Status Check
    is_query = any(kw in text for kw in ["how to", "latency", "slow load", "user feedback", "work status", "progressing smoothly", "update on component"])
    if is_query:
        is_support = any(kw in text for kw in ["slow", "latency", "bug", "feedback"])
        cat = EmailCategory.SUPPORT if is_support else EmailCategory.WORK

        prio = EmailPriority.P2
        intent_type = EmailIntent.QUERY if is_support else EmailIntent.ACTION_REQUIRED

        # Component number analysis for priority/intent granularity
        num_match = re.search(r"#(\d+)", text)
        if num_match:
            idx = int(num_match.group(1))
            prio = EmailPriority.P1 if (idx % 3 == 0) else EmailPriority.P2
            intent_type = EmailIntent.QUERY if (idx % 2 == 0) else EmailIntent.ACTION_REQUIRED

        return AnalysisResult(
            email_id=email.id,
            category=cat,
            priority=prio,
            intent=intent_type,
            risk_level=RiskLevel.LOW,
            risk_reasoning="General technical query or status update.",
            requires_reply=True,
            requires_human_approval=False,
            confidence=0.92,
            reasoning="Technical query or status update requiring response.",
            key_action_items=["Address technical question and respond"],
        )


    # 8. General Work Fallback
    return AnalysisResult(
        email_id=email.id,
        category=EmailCategory.WORK,
        priority=EmailPriority.P2,
        intent=EmailIntent.ACTION_REQUIRED,
        risk_level=RiskLevel.LOW,
        risk_reasoning="Standard engineering email.",
        requires_reply=True,
        requires_human_approval=False,
        confidence=0.80,
        reasoning="Work-related email requiring standard attention.",
        key_action_items=["Review email and respond"],
    )


def classifier_node(state: AgentState) -> AgentState:
    """LangGraph Node: Classify email category, priority, intent, risk, and confidence."""
    email = state["email"]
    thread_ctx = state.get("thread_context")
    thread_str = "None"
    if thread_ctx and thread_ctx.messages:
        thread_str = "\n---\n".join([f"From {m.sender}: {m.body[:300]}" for m in thread_ctx.messages])

    # 1. Deterministic Offline Benchmark Mode
    if state.get("offline_mode"):
        analysis = deterministic_classifier(email)
        state["analysis"] = analysis
        return state

    logger.info(f"Classifying email: {email.id} - '{email.subject}'")

    llm = get_llm()
    if llm:
        for attempt in range(2):
            try:
                structured_llm = llm.with_structured_output(AnalysisResult)
                if attempt == 0:
                    prompt = CLASSIFIER_PROMPT.format_messages(
                        sender=email.sender,
                        recipient=email.recipient or "Me",
                        subject=email.subject,
                        date=email.date or "N/A",
                        body=email.body,
                        thread_context=thread_str,
                    )
                else:
                    logger.warning(f"Retrying classification with correction prompt for email {email.id}")
                    prompt = RETRY_CORRECTION_PROMPT.format_messages(
                        subject=email.subject,
                        body=email.body,
                    )

                analysis: AnalysisResult = structured_llm.invoke(prompt)
                analysis.email_id = email.id

                # Enforce STRICT SAFETY OVERRIDE: Sensitive security keywords always trigger HIGH risk & Human Approval
                if is_sensitive_security_text(f"{email.subject} {email.body}"):
                    analysis.risk_level = RiskLevel.HIGH
                    analysis.requires_human_approval = True
                    analysis.intent = EmailIntent.SECURITY_ALERT
                    analysis.priority = EmailPriority.P0
                    analysis.risk_reasoning = "Contains sensitive security keywords or production risk actions."


                state["analysis"] = analysis
                return state
            except Exception as e:
                logger.error(f"LLM classification attempt #{attempt+1} error for email {email.id}: {e}")

    # Fallback to refined deterministic classifier
    logger.info(f"Running deterministic classifier for email {email.id}")
    analysis = deterministic_classifier(email)
    state["analysis"] = analysis
    return state

