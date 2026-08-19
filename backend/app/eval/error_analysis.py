import logging
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MisclassificationRecord(BaseModel):
    benchmark_id: str
    subject: str
    expected_intent: str
    predicted_intent: str
    expected_risk: str
    predicted_risk: str
    expected_priority: str
    predicted_priority: str
    reasoning: str
    confidence: float
    latency_ms: float


class ErrorAnalysisSummary(BaseModel):
    total_samples: int
    intent_failures: int
    risk_failures: int
    priority_failures: int
    top_intent_confusion_pairs: List[Dict[str, Any]] = Field(default_factory=list)
    top_risk_confusion_pairs: List[Dict[str, Any]] = Field(default_factory=list)
    top_priority_confusion_pairs: List[Dict[str, Any]] = Field(default_factory=list)
    high_risk_false_negatives: List[MisclassificationRecord] = Field(default_factory=list)
    sample_records: List[MisclassificationRecord] = Field(default_factory=list)


def build_confusion_matrix(expected_list: List[str], predicted_list: List[str], classes: List[str]) -> Dict[str, Dict[str, int]]:
    """Build a 2D confusion matrix dict mapping Expected -> Predicted -> Count."""
    matrix = {exp: {pred: 0 for pred in classes} for exp in classes}
    for exp, pred in zip(expected_list, predicted_list):
        # Normalize strings to match classes
        norm_exp = next((c for c in classes if c.lower() in exp.lower() or exp.lower() in c.lower()), classes[0])
        norm_pred = next((c for c in classes if c.lower() in pred.lower() or pred.lower() in c.lower()), classes[0])
        matrix[norm_exp][norm_pred] += 1
    return matrix


def calculate_per_class_metrics(matrix: Dict[str, Dict[str, int]], classes: List[str]) -> Dict[str, Dict[str, float]]:
    """Calculate Precision, Recall, F1, and Support per class."""
    results = {}
    for cls in classes:
        tp = matrix[cls][cls]
        fp = sum(matrix[other][cls] for other in classes if other != cls)
        fn = sum(matrix[cls][other] for other in classes if other != cls)
        support = sum(matrix[cls][other] for other in classes)

        precision = (tp / (tp + fp)) * 100.0 if (tp + fp) > 0 else 0.0
        recall = (tp / (tp + fn)) * 100.0 if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        results[cls] = {
            "precision": round(precision, 2),
            "recall": round(recall, 2),
            "f1": round(f1, 2),
            "support": support,
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
        }
    return results


def get_top_confusion_pairs(matrix: Dict[str, Dict[str, int]], classes: List[str], top_n: int = 5) -> List[Dict[str, Any]]:
    """Extract top expected -> predicted confusion pairs where expected != predicted."""
    pairs = []
    for exp in classes:
        for pred in classes:
            if exp != pred and matrix[exp][pred] > 0:
                pairs.append({
                    "expected": exp,
                    "predicted": pred,
                    "count": matrix[exp][pred],
                    "pair_label": f"{exp} -> {pred}",
                })
    pairs.sort(key=lambda x: x["count"], reverse=True)
    return pairs[:top_n]
