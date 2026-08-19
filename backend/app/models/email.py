from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class EmailCategory(str, Enum):
    WORK = "Work"
    URGENT = "Urgent"
    SUPPORT = "Support / Bug"
    NOTIFICATION = "Notification / CI-CD"
    NEWSLETTER = "Newsletter / Promo"
    PERSONAL = "Personal"


class EmailPriority(str, Enum):
    P0 = "P0 - Critical"
    P1 = "P1 - High"
    P2 = "P2 - Medium"
    P3 = "P3 - Low"


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High - Requires Human Review"


class EmailIntent(str, Enum):
    QUERY = "Technical Query"
    ACTION_REQUIRED = "Action Required / Task Request"
    FYI = "Informational / FYI"
    DECISION_NEEDED = "Decision Needed"
    SECURITY_ALERT = "Security Alert / Credential Exposure Risk"
    PROMOTIONAL = "Promotional / Marketing"


class EmailMessage(BaseModel):
    id: str = Field(..., description="Unique Gmail message ID")
    thread_id: str = Field(..., description="Gmail thread ID")
    sender: str = Field(..., description="Sender name and email address")
    recipient: Optional[str] = Field(None, description="Recipient email address")
    subject: str = Field(..., description="Subject line of the email")
    body: str = Field(..., description="Full text body content of the email")
    snippet: Optional[str] = Field(None, description="Short preview snippet")
    date: Optional[str] = Field(None, description="Date header or timestamp")
    is_unread: bool = Field(True, description="Whether the email is currently unread")
    labels: List[str] = Field(default_factory=list, description="Gmail labels attached to message")


class EmailThread(BaseModel):
    thread_id: str
    messages: List[EmailMessage] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    email_id: str = Field(..., description="ID of the analyzed email")
    category: EmailCategory = Field(..., description="Categorization of email")
    priority: EmailPriority = Field(..., description="Priority level")
    intent: EmailIntent = Field(default=EmailIntent.ACTION_REQUIRED, description="Primary intent of email")
    risk_level: RiskLevel = Field(default=RiskLevel.LOW, description="Risk classification level")
    risk_reasoning: Optional[str] = Field(None, description="Explanation for risk level")
    requires_reply: bool = Field(..., description="Whether a reply is required")
    requires_human_approval: bool = Field(default=False, description="Whether human approval is required before draft creation")
    confidence: float = Field(default=0.90, description="Classifier confidence score from 0.0 to 1.0")
    reasoning: str = Field(..., description="Concise explanation for priority and category")
    key_action_items: List[str] = Field(default_factory=list, description="Extracted action items for engineer")


class UserStyleMemory(BaseModel):
    tone: str = Field(default="Direct, technical, professional, and concise", description="Preferred response tone")
    greeting_template: str = Field(default="Hi,", description="Default email greeting style")
    signoff_template: str = Field(default="Best regards,\nEngineering", description="Default email sign-off")
    custom_rules: List[str] = Field(default_factory=list, description="Specific engineer rules (e.g. Never promise exact ETAs)")


class MCPContext(BaseModel):
    calendar_events: List[str] = Field(default_factory=list, description="Relevant calendar context")
    github_context: List[str] = Field(default_factory=list, description="Relevant PR / GitHub issue context")
    tool_notes: Optional[str] = Field(None, description="Notes from external MCP tool calls")


class DraftReply(BaseModel):
    email_id: str = Field(..., description="ID of the original email")
    thread_id: str = Field(..., description="Thread ID to maintain email chain")
    recipient: str = Field(..., description="Recipient to whom the reply will be drafted")
    subject: str = Field(..., description="Subject line for the draft reply (e.g. Re: Subject)")
    body: str = Field(..., description="Drafted concise reply text content")
    reasoning: Optional[str] = Field(None, description="Contextual notes on reply strategy")
    draft_id: Optional[str] = Field(None, description="Gmail Draft ID once created in Gmail")
    status: str = Field(default="created", description="Draft status: pending_approval, approved, or created")


class ProcessedEmailResponse(BaseModel):
    email: EmailMessage
    thread_context: Optional[EmailThread] = None
    analysis: Optional[AnalysisResult] = None
    draft: Optional[DraftReply] = None
    mcp_context: Optional[MCPContext] = None


class ExecutionTrace(BaseModel):
    id: str
    email_id: str
    thread_id: str
    intent: Optional[str] = "Action Required"
    priority: Optional[str] = "P1"
    risk: Optional[str] = "Low"
    decision: str
    confidence: float = 0.90
    agent_state: dict = Field(default_factory=dict)
    model_used: str = "gpt-4o-mini"
    processing_time_ms: float = 0.0
    draft_created: bool = False
    human_approved: Optional[bool] = None
    validation_result: str = "PASSED"
    created_at: Optional[str] = None


class EvalMetrics(BaseModel):
    id: str
    intent_accuracy: float
    risk_accuracy: float
    priority_accuracy: float
    validation_accuracy: float
    approval_precision: float
    false_positive_rate: float
    high_risk_precision: float = 100.0
    high_risk_recall: float = 100.0
    high_risk_f1: float = 100.0
    high_risk_false_negatives: int = 0
    avg_latency_ms: float
    total_samples: int
    metrics_json: dict = Field(default_factory=dict)
    created_at: Optional[str] = None



