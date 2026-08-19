import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.db import get_db, EvalRunRecord
from app.models.email import EvalMetrics
from app.eval.evaluator import AgentEvaluator
from app.core.security import verify_api_key

logger = logging.getLogger(__name__)

eval_router = APIRouter(prefix="/api/eval", tags=["Evaluation Pipeline"], dependencies=[Depends(verify_api_key)])


@eval_router.get("/latest", summary="Get Latest Evaluation Benchmark Results")
async def get_latest_eval(db: AsyncSession = Depends(get_db)):
    """Retrieve the most recent benchmark evaluation metrics run."""
    try:
        stmt = select(EvalRunRecord).order_by(EvalRunRecord.created_at.desc()).limit(1)
        res = await db.execute(stmt)
        record = res.scalar_one_or_none()

        if not record:
            # Run quick default evaluation if no stored run exists yet
            evaluator = AgentEvaluator()
            metrics = evaluator.run_evaluation(limit=50)
            
            new_rec = EvalRunRecord(
                id=metrics.id,
                intent_accuracy=str(metrics.intent_accuracy),
                risk_accuracy=str(metrics.risk_accuracy),
                priority_accuracy=str(metrics.priority_accuracy),
                validation_accuracy=str(metrics.validation_accuracy),
                approval_precision=str(metrics.approval_precision),
                false_positive_rate=str(metrics.false_positive_rate),
                avg_latency_ms=str(metrics.avg_latency_ms),
                total_samples=str(metrics.total_samples),
                metrics_json=metrics.metrics_json,
            )
            db.add(new_rec)
            await db.commit()
            return metrics

        return EvalMetrics(
            id=record.id,
            intent_accuracy=float(record.intent_accuracy),
            risk_accuracy=float(record.risk_accuracy),
            priority_accuracy=float(record.priority_accuracy),
            validation_accuracy=float(record.validation_accuracy),
            approval_precision=float(record.approval_precision),
            false_positive_rate=float(record.false_positive_rate),
            avg_latency_ms=float(record.avg_latency_ms),
            total_samples=int(record.total_samples),
            metrics_json=record.metrics_json or {},
            created_at=record.created_at.isoformat() if record.created_at else None,
        )
    except Exception as e:
        logger.error(f"Error fetching evaluation metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch evaluation metrics: {str(e)}")


@eval_router.post("/run", summary="Trigger Offline Evaluation Benchmark Run")
async def trigger_eval_run(limit: int = Query(100, ge=5, le=100), db: AsyncSession = Depends(get_db)):
    """Run offline evaluation suite across benchmark email dataset."""
    try:
        evaluator = AgentEvaluator()
        metrics = evaluator.run_evaluation(limit=limit)

        new_rec = EvalRunRecord(
            id=metrics.id,
            intent_accuracy=str(metrics.intent_accuracy),
            risk_accuracy=str(metrics.risk_accuracy),
            priority_accuracy=str(metrics.priority_accuracy),
            validation_accuracy=str(metrics.validation_accuracy),
            approval_precision=str(metrics.approval_precision),
            false_positive_rate=str(metrics.false_positive_rate),
            avg_latency_ms=str(metrics.avg_latency_ms),
            total_samples=str(metrics.total_samples),
            metrics_json=metrics.metrics_json,
        )
        db.add(new_rec)
        await db.commit()

        return {"status": "success", "message": "Evaluation pipeline completed successfully.", "metrics": metrics}
    except Exception as e:
        logger.error(f"Error executing evaluation run: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
