# Gmail Copilot — Agent Workflow & LangGraph Design

## State Management

The agent uses a centralized Pydantic state model (`AgentState`):

```python
class AgentState(TypedDict):
    email: EmailMessage
    thread_context: Optional[EmailThread]
    analysis: Optional[AnalysisResult]
    mcp_context: Optional[MCPContext]
    user_style: Optional[UserStyleMemory]
    draft: Optional[DraftReply]
    validation_status: Optional[str]
    start_time_ms: float
    error: Optional[str]
```

---

## Tool Execution Policies

Tools are executed conditionally based on planner classification:
- **Gmail Tool**: Always active for thread history retrieval & draft creation.
- **Calendar Tool**: Invoked only when `requires_calendar = True` (e.g. interview / meeting scheduling).
- **GitHub Tool**: Invoked only when `requires_github = True` (e.g. PR status / issue lookups).

---

## RAG Style Memory Pipeline

```text
Approved Replies
      │
      ▼
Normalize & Chunk
      │
      ▼
Embedding Match (Cosine Similarity)
      │
      ▼
Inject Style Guidelines into System Prompt
```
