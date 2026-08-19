# Gmail Copilot — System Architecture & Design Specification

## Overview

Gmail Copilot is an enterprise-oriented, security-hardened agentic AI system for managing email communication. It combines structured classification, thread context building, external MCP tool querying, RAG-based writing style memory, deterministic safety gatekeeping, and human-in-the-loop approval workflows.

---

## 🏗️ Core Architecture Components

```
                                SYSTEM ARCHITECTURE

 ┌─────────────────────────────────────────────────────────────────────────────────────────┐
 │                                                                                         │
 │     React TS Dashboard                CORS / Security Headers / X-API-Key                 │
 │     (Observability / Eval) ────────► FastAPI Backend (Gunicorn/Uvicorn)                 │
 │                                                  │                                      │
 │                                                  ▼                                      │
 │                                      LangGraph Agent Workflow                           │
 │                                                  │                                      │
 │       ┌───────────────────┬──────────────────────┼──────────────────────┬─────────────┐ │
 │       ▼                   ▼                      ▼                      ▼             ▼ │
 │  Thread Builder       MCP Context         Classifier Node          Style Memory   Validator │
 │  (Gmail History)     (Calendar/GitHub)    - P0-P3 Criteria         (RAG Memory)   (Safety)  │
 │                                           - Safety Gate                                 │
 │                                                  │                                      │
 │                                                  ▼                                      │
 │                                        Confidence-Aware Router                          │
 │                                   ┌──────────────┼──────────────┐                       │
 │                                   ▼              ▼              ▼                       │
 │                             High Risk /      Confidence    Confidence                   │
 │                             Security Rule     0.60-0.85      >= 0.85                    │
 │                                   │              │              │                       │
 │                                   ▼              ▼              ▼                       │
 │                             Human Review    Verification    Auto-Draft                  │
 │                                Queue            Path          Workflow                  │
 │                                                                                         │
 └─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1. API Layer (`FastAPI`)
- **Endpoints**: Health, OAuth status, batch email processing, draft creation, execution traces, user style memory, evaluation runners, and demo scenarios.
- **Middleware**: Rate limiting (sliding window), security headers (`nosniff`, `DENY`, `HSTS`), CORS white-list, `X-API-Key` authentication.

### 2. Orchestration Layer (`LangGraph`)
Stateful workflow executing isolated nodes:
- `thread_builder`: History lookup & thread formatting.
- `mcp_context`: Google Calendar & GitHub REST API lookup.
- `classify`: Intent, priority, and risk classification.
- `style_memory`: RAG tone memory lookup.
- `generate_reply`: Grounded draft synthesis.
- `validate_reply`: Pre-send security validator.
- `router`: Confidence & safety-aware decision router.

### 3. Database Layer (`PostgreSQL` + `SQLAlchemy 2.0`)
- Asyncpg connection pooling with Alembic migrations.
- Tables: `users`, `oauth_accounts`, `email_threads`, `emails`, `agent_runs`, `agent_nodes`, `tool_calls`, `reply_drafts`, `approval_queue`, `style_memory`, `evaluation_runs`, `evaluation_cases`, `security_events`.

### 4. Frontend Layer (`React 18` + `TypeScript` + `Vite`)
- Modern light SaaS dashboard displaying live inbox, approval queue, execution traces, style preferences, evaluation benchmarks, and 5 interactive recruiter demo scenarios.
