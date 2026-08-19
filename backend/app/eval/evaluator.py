import os
import json
import time
import logging
import uuid
import hashlib
import numpy as np
from typing import List, Dict, Any, Tuple
from app.config import settings
from app.models.email import EmailMessage, EvalMetrics
from app.agent.graph import email_agent_graph
from app.agent.state import AgentState
from app.eval.error_analysis import (
    build_confusion_matrix,
    calculate_per_class_metrics,
    get_top_confusion_pairs,
    MisclassificationRecord,
)

logger = logging.getLogger(__name__)

INTENT_CLASSES = [
    "Technical Query",
    "Action Required / Task Request",
    "Informational / FYI",
    "Decision Needed",
    "Security Alert / Credential Exposure Risk",
    "Promotional / Marketing",
]

RISK_CLASSES = [
    "Low",
    "Medium",
    "High - Requires Human Review",
]

PRIORITY_CLASSES = [
    "P0 - Critical",
    "P1 - High",
    "P2 - Medium",
    "P3 - Low",
]


class AgentEvaluator:
    """Offline Evaluation Pipeline measuring Dev vs Holdout generalization, safety precision, node latency, and confusion matrices."""

    def __init__(self, dataset_path: str = settings.EVAL_DATASET_PATH):
        self.dataset_path = dataset_path
        self.holdout_path = os.path.join(os.path.dirname(__file__), "holdout_dataset.json")
        self.manifest_path = os.path.join(os.path.dirname(__file__), "holdout_manifest.json")

    def verify_holdout_integrity(self) -> bool:
        """Verify holdout dataset cryptographic SHA-256 hash match against manifest."""
        if not os.path.exists(self.holdout_path) or not os.path.exists(self.manifest_path):
            logger.error("Holdout dataset or manifest missing.")
            return False

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        with open(self.holdout_path, "rb") as f:
            content = f.read()

        current_hash = hashlib.sha256(content).hexdigest()
        expected_hash = manifest.get("sha256_hash")

        if current_hash != expected_hash:
            logger.error(f"Holdout SHA-256 mismatch! Expected {expected_hash}, got {current_hash}")
            return False
        return True

    def load_dataset(self, path: str = None) -> List[Dict[str, Any]]:
        """Load benchmark dataset from path."""
        target_path = path or self.dataset_path
        if not os.path.exists(target_path):
            logger.error(f"Evaluation dataset file missing at {target_path}")
            return []
        with open(target_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def run_dataset_eval(self, dataset: List[Dict[str, Any]], eval_type: str = "Dev") -> EvalMetrics:
        """Core evaluation suite running across test samples and computing full metrics."""
        logger.info(f"Starting {eval_type} Evaluation Pipeline on {len(dataset)} emails...")

        intent_expected = []
        intent_predicted = []

        risk_expected = []
        risk_predicted = []

        priority_expected = []
        priority_predicted = []

        misclassifications: List[MisclassificationRecord] = []
        high_risk_false_negs: List[MisclassificationRecord] = []

        validation_passed = 0
        total_drafts = 0

        true_positives_approval = 0
        false_positives_approval = 0
        false_negatives_approval = 0
        true_negatives_approval = 0

        processing_times: List[float] = []
        node_timing_history: Dict[str, List[float]] = {
            "thread_builder": [],
            "mcp_context": [],
            "classify": [],
            "style_memory": [],
            "generate_reply": [],
            "validate_reply": [],
        }

        for sample in dataset:
            email = EmailMessage(
                id=sample["id"],
                thread_id=f"thread_{sample['id']}",
                sender=sample["sender"],
                subject=sample["subject"],
                body=sample["body"],
                snippet=sample["body"][:100],
                is_unread=True,
            )

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
                "node_latencies": {},
                "node_retry_counts": {},
                "offline_mode": True,
                "error": None,
            }

            try:
                final_state = email_agent_graph.invoke(initial_state)
                elapsed_ms = (time.time() - start_t) * 1000
                processing_times.append(elapsed_ms)

                analysis = final_state.get("analysis")
                draft = final_state.get("draft")
                val_status = final_state.get("validation_status") or "PASSED"
                node_latencies = final_state.get("node_latencies") or {}

                for node_k, dur_v in node_latencies.items():
                    if node_k in node_timing_history:
                        node_timing_history[node_k].append(dur_v)

                exp_intent = sample["expected_intent"]
                exp_risk = sample["expected_risk"]
                exp_prio = sample["expected_priority"]

                pred_intent = analysis.intent.value if (analysis and hasattr(analysis.intent, "value")) else str(getattr(analysis, "intent", ""))
                pred_risk = analysis.risk_level.value if (analysis and hasattr(analysis.risk_level, "value")) else str(getattr(analysis, "risk_level", ""))
                pred_prio = analysis.priority.value if (analysis and hasattr(analysis.priority, "value")) else str(getattr(analysis, "priority", ""))

                intent_expected.append(exp_intent)
                intent_predicted.append(pred_intent)

                risk_expected.append(exp_risk)
                risk_predicted.append(pred_risk)

                priority_expected.append(exp_prio)
                priority_predicted.append(pred_prio)

                # Check for misclassification
                is_intent_wrong = exp_intent.lower() not in pred_intent.lower() and pred_intent.lower() not in exp_intent.lower()
                is_risk_wrong = exp_risk.lower() not in pred_risk.lower() and pred_risk.lower() not in exp_risk.lower()
                is_prio_wrong = exp_prio.lower() not in pred_prio.lower() and pred_prio.lower() not in exp_prio.lower()

                if is_intent_wrong or is_risk_wrong or is_prio_wrong:
                    record = MisclassificationRecord(
                        benchmark_id=sample["id"],
                        subject=sample["subject"],
                        expected_intent=exp_intent,
                        predicted_intent=pred_intent,
                        expected_risk=exp_risk,
                        predicted_risk=pred_risk,
                        expected_priority=exp_prio,
                        predicted_priority=pred_prio,
                        reasoning=getattr(analysis, "reasoning", "N/A") if analysis else "No analysis",
                        confidence=getattr(analysis, "confidence", 0.0) if analysis else 0.0,
                        latency_ms=round(elapsed_ms, 1),
                    )
                    misclassifications.append(record)

                    if "high" in exp_risk.lower() and "high" not in pred_risk.lower():
                        high_risk_false_negs.append(record)

                # Check Validation
                if draft:
                    total_drafts += 1
                    if "PASSED" in val_status:
                        validation_passed += 1

                # Check Approval Precision / Recall
                actual_req_approval = analysis.requires_human_approval if analysis else False
                expected_req_approval = sample["expected_requires_approval"]

                if actual_req_approval and expected_req_approval:
                    true_positives_approval += 1
                elif actual_req_approval and not expected_req_approval:
                    false_positives_approval += 1
                elif not actual_req_approval and expected_req_approval:
                    false_negatives_approval += 1
                else:
                    true_negatives_approval += 1

            except Exception as e:
                logger.error(f"Error evaluating sample {sample['id']}: {e}")

        N = len(dataset)

        # Build Confusion Matrices
        intent_cm = build_confusion_matrix(intent_expected, intent_predicted, INTENT_CLASSES)
        risk_cm = build_confusion_matrix(risk_expected, risk_predicted, RISK_CLASSES)
        prio_cm = build_confusion_matrix(priority_expected, priority_predicted, PRIORITY_CLASSES)

        # Calculate Per-Class Metrics
        intent_class_metrics = calculate_per_class_metrics(intent_cm, INTENT_CLASSES)
        risk_class_metrics = calculate_per_class_metrics(risk_cm, RISK_CLASSES)
        prio_class_metrics = calculate_per_class_metrics(prio_cm, PRIORITY_CLASSES)

        # Overall Accuracy Calculations
        intent_correct = sum(intent_cm[c][c] for c in INTENT_CLASSES)
        risk_correct = sum(risk_cm[c][c] for c in RISK_CLASSES)
        prio_correct = sum(prio_cm[c][c] for c in PRIORITY_CLASSES)

        intent_acc = (intent_correct / N) * 100.0
        risk_acc = (risk_correct / N) * 100.0
        prio_acc = (prio_correct / N) * 100.0
        val_acc = (validation_passed / max(1, total_drafts)) * 100.0

        # HIGH-Risk Specific Metrics
        high_class = "High - Requires Human Review"
        high_risk_prec = risk_class_metrics.get(high_class, {}).get("precision", 100.0)
        high_risk_rec = risk_class_metrics.get(high_class, {}).get("recall", 100.0)
        high_risk_f1_val = risk_class_metrics.get(high_class, {}).get("f1", 100.0)
        high_risk_fn_cnt = len(high_risk_false_negs)

        approval_prec = (
            (true_positives_approval / (true_positives_approval + false_positives_approval)) * 100.0
            if (true_positives_approval + false_positives_approval) > 0
            else 100.0
        )
        fp_rate = (
            (false_positives_approval / (false_positives_approval + true_negatives_approval)) * 100.0
            if (false_positives_approval + true_negatives_approval) > 0
            else 0.0
        )

        avg_time = sum(processing_times) / max(1, len(processing_times))

        # Calculate Node-Level Latency P50, P95, P99
        node_latency_stats = {}
        for node_name, timings in node_timing_history.items():
            if timings:
                arr = np.array(timings)
                node_latency_stats[node_name] = {
                    "avg": round(float(np.mean(arr)), 1),
                    "p50": round(float(np.percentile(arr, 50)), 1),
                    "p95": round(float(np.percentile(arr, 95)), 1),
                    "p99": round(float(np.percentile(arr, 99)), 1),
                }
            else:
                node_latency_stats[node_name] = {"avg": 0.0, "p50": 0.0, "p95": 0.0, "p99": 0.0}

        # Identify Top 3 Latency Contributing Nodes
        sorted_nodes = sorted(node_latency_stats.items(), key=lambda x: x[1]["avg"], reverse=True)
        top_3_latency_nodes = [n[0] for n in sorted_nodes[:3]]

        # Top Confusion Pairs
        top_intent_pairs = get_top_confusion_pairs(intent_cm, INTENT_CLASSES)
        top_risk_pairs = get_top_confusion_pairs(risk_cm, RISK_CLASSES)
        top_prio_pairs = get_top_confusion_pairs(prio_cm, PRIORITY_CLASSES)

        eval_id = f"eval_{eval_type.lower()}_{uuid.uuid4().hex[:8]}"

        metrics = EvalMetrics(
            id=eval_id,
            intent_accuracy=round(intent_acc, 2),
            risk_accuracy=round(risk_acc, 2),
            priority_accuracy=round(prio_acc, 2),
            validation_accuracy=round(val_acc, 2),
            approval_precision=round(approval_prec, 2),
            false_positive_rate=round(fp_rate, 2),
            high_risk_precision=round(high_risk_prec, 2),
            high_risk_recall=round(high_risk_rec, 2),
            high_risk_f1=round(high_risk_f1_val, 2),
            high_risk_false_negatives=high_risk_fn_cnt,
            avg_latency_ms=round(avg_time, 1),
            total_samples=N,
            metrics_json={
                "eval_type": eval_type,
                "confusion_matrices": {
                    "intent": intent_cm,
                    "risk": risk_cm,
                    "priority": prio_cm,
                },
                "per_class_metrics": {
                    "intent": intent_class_metrics,
                    "risk": risk_class_metrics,
                    "priority": prio_class_metrics,
                },
                "node_latency_stats": node_latency_stats,
                "top_3_latency_nodes": top_3_latency_nodes,
                "top_confusion_pairs": {
                    "intent": top_intent_pairs,
                    "risk": top_risk_pairs,
                    "priority": top_prio_pairs,
                },
                "total_misclassifications": len(misclassifications),
                "high_risk_false_negatives_count": high_risk_fn_cnt,
            },
        )

        return metrics

    def run_evaluation(self, limit: int = 100) -> EvalMetrics:
        """Run Dev benchmark evaluation suite (100 emails)."""
        dataset = self.load_dataset(self.dataset_path)[:limit]
        if not dataset:
            raise ValueError("Dev dataset empty or missing.")
        return self.run_dataset_eval(dataset, eval_type="Dev")

    def run_holdout_evaluation(self) -> Tuple[EvalMetrics, bool]:
        """Run Unseen Holdout benchmark evaluation suite (50 emails) with SHA-256 integrity verification."""
        is_valid = self.verify_holdout_integrity()
        if not is_valid:
            logger.warning("Holdout SHA-256 integrity check failed!")

        holdout_data = self.load_dataset(self.holdout_path)
        if not holdout_data:
            raise ValueError("Holdout dataset empty or missing.")

        metrics = self.run_dataset_eval(holdout_data, eval_type="Holdout")
        return metrics, is_valid
