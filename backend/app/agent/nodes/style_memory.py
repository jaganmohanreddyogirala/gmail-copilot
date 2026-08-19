import logging
from typing import List, Dict
from app.agent.state import AgentState
from app.models.email import UserStyleMemory

logger = logging.getLogger(__name__)

DEFAULT_STYLE_EXAMPLES = [
    {
        "intent": "Action Required",
        "rules": [
            "Keep replies concise and under 4 sentences.",
            "Use a professional yet direct engineer tone.",
            "Avoid fluff, unnecessary pleasantries, or generic placeholders.",
            "Explicitly state clear next steps or resolution status.",
        ],
    },
    {
        "intent": "Technical Query",
        "rules": [
            "Answer technical questions directly with code/docs reference when available.",
            "Maintain short paragraphs.",
            "Do not promise unverified ETAs or uncommitted architectural changes.",
        ],
    },
    {
        "intent": "Decision Needed",
        "rules": [
            "Summarize options clearly.",
            "State recommended technical approach first.",
            "Keep greeting minimal ('Hi,').",
        ],
    },
]


def retrieve_user_style_memory(intent: str, category: str) -> UserStyleMemory:
    """RAG retriever matching incoming email intent & category to relevant user style guidelines."""
    logger.info(f"RAG Style Memory Retriever: Fetching style rules for intent '{intent}', category '{category}'")

    matched_rules: List[str] = [
        "Concise replies (short paragraphs).",
        "Professional engineering tone.",
        "Direct answers with minimal greetings.",
        "No unnecessary pleasantries or filler text.",
    ]

    for item in DEFAULT_STYLE_EXAMPLES:
        if item["intent"].lower() in intent.lower():
            matched_rules.extend(item["rules"])

    return UserStyleMemory(
        tone="Direct, concise, professional software engineer tone",
        greeting_template="Hi,",
        signoff_template="Best regards,\nEngineering",
        custom_rules=list(set(matched_rules)),
    )


def style_memory_node(state: AgentState) -> AgentState:
    """LangGraph Node: Retrieve and attach user style context before generating reply."""
    analysis = state.get("analysis")
    intent = analysis.intent.value if (analysis and analysis.intent) else "Action Required"
    category = analysis.category.value if (analysis and analysis.category) else "Work"

    style_memory = retrieve_user_style_memory(intent=intent, category=category)
    state["user_style"] = style_memory
    logger.info(f"Style Memory Node: Attached {len(style_memory.custom_rules)} dynamic style rules.")
    return state
