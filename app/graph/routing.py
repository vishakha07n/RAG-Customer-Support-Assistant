from app.graph.state import AgentState
from app.utils.logger import get_logger

logger = get_logger(__name__)

def route_after_analysis(state: AgentState) -> str:
    """
    Conditional routing function used by LangGraph to determine the next node based on state['route'].
    """
    # Fallback ONLY when: no documents retrieved OR confidence < threshold
    if not state.get("retrieved_chunks") or state.get("confidence_score", 0.0) < 0.1:
        logger.info("Confidence too low or no chunks. Forcing fallback.")
        return "fallback"

    route = state.get("route", "answer")
    logger.info(f"LLM suggested route: {route}")
    
    if route == "clarify":
        return "clarify"
    elif route == "escalate":
        return "escalate"
    
    # If chunks exist and confidence >= threshold, WE MUST ANSWER.
    # Do not allow LLM to trigger fallback here.
    return "generate_answer"
