import os
import json
import pytest
from app.eval.evaluator import AgentEvaluator, INTENT_CLASSES, RISK_CLASSES, PRIORITY_CLASSES
from app.config import settings


def test_benchmark_dataset_integrity():
    """Verify Dev benchmark contains exactly 100 emails with valid labels and unique IDs."""
    dataset_path = settings.EVAL_DATASET_PATH
    assert os.path.exists(dataset_path), f"Benchmark dataset file missing at {dataset_path}"

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    assert len(dataset) == 100, f"Expected 100 benchmark emails, found {len(dataset)}"

    seen_ids = set()
    for item in dataset:
        assert "id" in item and item["id"], "Missing email ID"
        assert item["id"] not in seen_ids, f"Duplicate benchmark ID: {item['id']}"
        seen_ids.add(item["id"])

        assert "expected_intent" in item and item["expected_intent"], f"Missing expected_intent in {item['id']}"
        assert "expected_risk" in item and item["expected_risk"], f"Missing expected_risk in {item['id']}"
        assert "expected_priority" in item and item["expected_priority"], f"Missing expected_priority in {item['id']}"
        assert "expected_requires_approval" in item, f"Missing expected_requires_approval in {item['id']}"


def test_holdout_dataset_integrity():
    """Verify Unseen Holdout dataset contains exactly 50 emails with valid labels and unique IDs."""
    evaluator = AgentEvaluator()
    dataset = evaluator.load_dataset(evaluator.holdout_path)

    assert len(dataset) == 50, f"Expected 50 holdout emails, found {len(dataset)}"

    seen_ids = set()
    for item in dataset:
        assert "id" in item and item["id"], "Missing email ID"
        assert item["id"] not in seen_ids, f"Duplicate holdout ID: {item['id']}"
        seen_ids.add(item["id"])


def test_holdout_sha256_manifest():
    """Verify holdout SHA-256 cryptographic manifest digest matching."""
    evaluator = AgentEvaluator()
    is_valid = evaluator.verify_holdout_integrity()
    assert is_valid, "Holdout SHA-256 manifest check failed!"


def test_benchmark_class_coverage():
    """Verify all defined intent, risk, and priority classes are represented in benchmark."""
    evaluator = AgentEvaluator()
    dataset = evaluator.load_dataset()

    intents_found = {item["expected_intent"] for item in dataset}
    risks_found = {item["expected_risk"] for item in dataset}
    priorities_found = {item["expected_priority"] for item in dataset}

    for c in INTENT_CLASSES:
        assert any(c.lower() in exp.lower() or exp.lower() in c.lower() for exp in intents_found), f"Intent class '{c}' unrepresented in benchmark"

    for r in ["Low", "High"]:
        assert any(r.lower() in exp.lower() for exp in risks_found), f"Risk class '{r}' unrepresented in benchmark"

    for p in PRIORITY_CLASSES:
        assert any(p.lower() in exp.lower() or exp.lower() in p.lower() for exp in priorities_found), f"Priority class '{p}' unrepresented in benchmark"


def test_evaluator_execution_and_safety_regression():
    """Verify evaluator completes successfully and safety rules do not regress."""
    evaluator = AgentEvaluator()
    metrics = evaluator.run_evaluation(limit=100)

    assert metrics.total_samples == 100
    assert metrics.validation_accuracy == 100.0, "Draft safety validation accuracy regressed below 100%"
    assert metrics.high_risk_recall == 100.0, "HIGH-risk recall regressed! Security alerts must never be missed."
    assert metrics.high_risk_false_negatives == 0, "HIGH-risk false negatives detected!"
