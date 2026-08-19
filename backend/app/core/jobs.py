import logging
import time
import uuid
import datetime
from typing import Optional, Dict, Any, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.db import JobRecord

logger = logging.getLogger(__name__)


async def create_job(db: AsyncSession, job_type: str) -> JobRecord:
    """Create persistent background job record in PENDING state."""
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    job = JobRecord(
        id=job_id,
        job_type=job_type,
        status="PENDING",
        attempt_count={"count": 0},
        created_at=datetime.datetime.utcnow(),
    )
    try:
        db.add(job)
        await db.commit()
        await db.refresh(job)
        logger.info(f"Created background job {job_id} ({job_type})")
    except Exception as e:
        logger.error(f"Failed to create job: {e}")
        await db.rollback()
    return job


async def update_job_status(
    db: AsyncSession,
    job_id: str,
    status: str,
    error_message: Optional[str] = None,
    attempt: int = 1,
) -> Optional[JobRecord]:
    """Update status, timestamps, and retry counts for persistent job."""
    try:
        stmt = select(JobRecord).where(JobRecord.id == job_id)
        res = await db.execute(stmt)
        job = res.scalar_one_or_none()
        if not job:
            return None

        job.status = status
        job.attempt_count = {"count": attempt}

        if status == "RUNNING" and not job.started_at:
            job.started_at = datetime.datetime.utcnow()
        elif status in ["COMPLETED", "FAILED"]:
            job.completed_at = datetime.datetime.utcnow()

        if error_message:
            job.error_message = str(error_message)

        await db.commit()
        await db.refresh(job)
        logger.info(f"Updated job {job_id} status -> {status}")
        return job
    except Exception as e:
        logger.error(f"Failed to update job status: {e}")
        await db.rollback()
        return None
