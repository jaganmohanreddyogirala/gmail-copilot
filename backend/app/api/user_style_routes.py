import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.db import get_db, UserStyleRecord
from app.models.email import UserStyleMemory
from app.core.security import verify_api_key

logger = logging.getLogger(__name__)

style_router = APIRouter(prefix="/api/user-style", tags=["User Style Memory"], dependencies=[Depends(verify_api_key)])


@style_router.get("", response_model=UserStyleMemory, summary="Get User Style Memory Rules")
async def get_user_style(db: AsyncSession = Depends(get_db)):
    """Retrieve active user style memory preferences."""
    try:
        stmt = select(UserStyleRecord).where(UserStyleRecord.id == "default")
        res = await db.execute(stmt)
        record = res.scalar_one_or_none()

        if not record:
            return UserStyleMemory()

        return UserStyleMemory(
            tone=record.tone,
            greeting_template=record.greeting_template,
            signoff_template=record.signoff_template,
            custom_rules=record.custom_rules or [],
        )
    except Exception as e:
        logger.error(f"Error fetching user style: {e}")
        return UserStyleMemory()


@style_router.post("", summary="Update User Style Memory Rules")
async def update_user_style(style: UserStyleMemory, db: AsyncSession = Depends(get_db)):
    """Update active user style memory preferences."""
    try:
        stmt = select(UserStyleRecord).where(UserStyleRecord.id == "default")
        res = await db.execute(stmt)
        record = res.scalar_one_or_none()

        if not record:
            record = UserStyleRecord(
                id="default",
                tone=style.tone,
                greeting_template=style.greeting_template,
                signoff_template=style.signoff_template,
                custom_rules=style.custom_rules,
            )
            db.add(record)
        else:
            record.tone = style.tone
            record.greeting_template = style.greeting_template
            record.signoff_template = style.signoff_template
            record.custom_rules = style.custom_rules

        await db.commit()
        logger.info("Updated User Style Memory preferences.")
        return {"status": "success", "message": "User style memory updated successfully.", "style": style}
    except Exception as e:
        logger.error(f"Failed to update user style memory: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save style memory: {str(e)}")
