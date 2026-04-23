from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    """
    LangGraph State object tracking variables across the execution flow.
    """
    session_id: str
    user_query: str
    retrieved_chunks: List[Dict[str, Any]]
    context_string: str
    route: str  # answer, clarify, fallback, escalate
    routing_reason: str
    answer_draft: str
    confidence_score: float
    escalation_required: bool
    escalation_ticket: Optional[Dict[str, Any]]
    human_decision: Optional[str]
    human_custom_reply: Optional[str]
    final_response: str
    sources: List[Dict[str, Any]]
    error: Optional[str]
