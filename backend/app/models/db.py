import datetime
from typing import AsyncGenerator
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings

Base = declarative_base()


class EmailRecord(Base):
    __tablename__ = "emails"

    id = Column(String(255), primary_key=True, index=True)
    thread_id = Column(String(255), nullable=False, index=True)
    sender = Column(String(500), nullable=False)
    recipient = Column(String(500), nullable=True)
    subject = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    snippet = Column(Text, nullable=True)
    date = Column(String(255), nullable=True)
    is_unread = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    analysis = relationship("AnalysisRecord", back_populates="email", uselist=False, cascade="all, delete-orphan")
    draft = relationship("DraftRecord", back_populates="email", uselist=False, cascade="all, delete-orphan")


class AnalysisRecord(Base):
    __tablename__ = "analyses"

    id = Column(String(255), primary_key=True, index=True)
    email_id = Column(String(255), ForeignKey("emails.id"), nullable=False, unique=True)
    category = Column(String(100), nullable=False)
    priority = Column(String(100), nullable=False)
    intent = Column(String(100), nullable=True, default="Action Required")
    risk_level = Column(String(100), nullable=True, default="Low")
    risk_reasoning = Column(Text, nullable=True)
    requires_reply = Column(Boolean, nullable=False)
    requires_human_approval = Column(Boolean, default=False)
    reasoning = Column(Text, nullable=False)
    key_action_items = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    email = relationship("EmailRecord", back_populates="analysis")


class DraftRecord(Base):
    __tablename__ = "drafts"

    id = Column(String(255), primary_key=True, index=True)
    email_id = Column(String(255), ForeignKey("emails.id"), nullable=False, unique=True)
    draft_id = Column(String(255), nullable=True)  # Gmail Draft ID
    thread_id = Column(String(255), nullable=False)
    recipient = Column(String(500), nullable=False)
    subject = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    reasoning = Column(Text, nullable=True)
    status = Column(String(50), default="created")  # pending_approval, approved, created
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    email = relationship("EmailRecord", back_populates="draft")


class ApprovalQueueRecord(Base):
    __tablename__ = "approval_queue"

    id = Column(String(255), primary_key=True, index=True)
    email_id = Column(String(255), ForeignKey("emails.id"), nullable=False)
    draft_body = Column(Text, nullable=False)
    risk_level = Column(String(100), nullable=False)
    risk_reasoning = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, approved, rejected
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class UserStyleRecord(Base):
    __tablename__ = "user_styles"

    id = Column(String(255), primary_key=True, default="default")
    tone = Column(Text, nullable=False)
    greeting_template = Column(String(255), nullable=False)
    signoff_template = Column(Text, nullable=False)
    custom_rules = Column(JSON, default=list)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class ExecutionTraceRecord(Base):
    __tablename__ = "execution_traces"

    id = Column(String(255), primary_key=True, index=True)
    email_id = Column(String(255), nullable=False, index=True)
    thread_id = Column(String(255), nullable=False)
    intent = Column(String(100), nullable=True)
    priority = Column(String(100), nullable=True)
    risk = Column(String(100), nullable=True)
    decision = Column(String(100), nullable=False)
    agent_state = Column(JSON, default=dict)
    model_used = Column(String(100), nullable=False, default="gpt-4o-mini")
    processing_time_ms = Column(Text, nullable=False, default="0")
    draft_created = Column(Boolean, default=False)
    human_approved = Column(Boolean, nullable=True)
    validation_result = Column(String(100), default="PASSED")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class JobRecord(Base):
    __tablename__ = "jobs"

    id = Column(String(255), primary_key=True, index=True)
    job_type = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="PENDING", index=True)  # PENDING, RUNNING, RETRYING, COMPLETED, FAILED
    attempt_count = Column(JSON, default=dict)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)


class EvalRunRecord(Base):
    __tablename__ = "eval_runs"

    id = Column(String(255), primary_key=True, index=True)
    intent_accuracy = Column(Text, nullable=False)
    risk_accuracy = Column(Text, nullable=False)
    priority_accuracy = Column(Text, nullable=False)
    validation_accuracy = Column(Text, nullable=False)
    approval_precision = Column(Text, nullable=False)
    false_positive_rate = Column(Text, nullable=False)
    avg_latency_ms = Column(Text, nullable=False)
    total_samples = Column(Text, nullable=False)
    metrics_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)





# Async Engine & Session Factory with fallback to SQLite
def get_engine():
    db_url = settings.DATABASE_URL
    try:
        return create_async_engine(db_url, echo=False)
    except Exception:
        return create_async_engine("sqlite+aiosqlite:///./gmail_copilot.db", echo=False)

engine = get_engine()
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Create database tables if they do not exist."""
    global engine, AsyncSessionLocal
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        # Fallback to SQLite if primary DB (e.g. Postgres) fails to connect
        engine = create_async_engine("sqlite+aiosqlite:///./gmail_copilot.db", echo=False)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing async database session with automatic in-memory fallback."""
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except Exception as e:
        # If primary DB connection fails, provide fallback SQLite in-memory session
        fallback_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        FallbackSession = async_sessionmaker(fallback_engine, class_=AsyncSession, expire_on_commit=False)
        async with fallback_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with FallbackSession() as fallback_session:
            yield fallback_session


