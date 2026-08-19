# Gmail Copilot — Evaluation Methodology & Offline Benchmark

## Evaluation Philosophy

Gmail Copilot includes a reproducible, offline evaluation framework (`scripts/run_eval.py`) that evaluates model classification accuracy, safety precision, and node-level latencies without calling external network APIs.

---

## 📊 Datasets & Manifest Isolation

- **Development Set (`dev_dataset.json`)**: 100 benchmark emails used for iterative prompt and classifier development.
- **Unseen Holdout Set (`holdout_dataset.json`)**: 50 emails reserved exclusively for generalization evaluation.
- **SHA-256 Manifest (`holdout_manifest.json`)**: Cryptographically locks the holdout dataset to guarantee dataset immutability (`9bdac11b7f8a3ac3b1f7420dfe8cb0a56a31a1e4303dd57e558c4c703c8273f7`).

---

## 📈 Evaluation Metrics Summary

| Evaluation Metric | Dev Set (100 Emails) | Unseen Holdout Set (50 Emails) | Generalization Gap |
| :--- | :---: | :---: | :---: |
| **Intent Accuracy** | `100.00%` | `54.00%` | `46.00 pp` |
| **Risk Accuracy** | `100.00%` | `100.00%` | `0.00 pp` |
| **Priority Accuracy** | `100.00%` | `68.00%` | `32.00 pp` |
| **Draft Validation Accuracy** | `100.00%` | `100.00%` | `0.00 pp` |
| **HIGH-Risk Recall** | `100.00%` | `100.00%` | `0.00 pp` |
| **HIGH-Risk False Negatives** | `0` | `0` | `0` |

---

## ⏱️ Latency Profiles

- **Offline Benchmark Latency**: `1.8 ms / email` (Mock components for zero network overhead).
- **Live External-Service Latency**: `~3,678.6 ms / email` (Real Gmail API + LLM API + MCP network latency).
