from app.graph.state import AgentState
from app.rag.retriever import Retriever
from app.llm.generator import LLMGenerator
from app.hitl.escalation import EscalationManager
from app.utils.logger import get_logger

logger = get_logger(__name__)

def retrieve_node(state: AgentState) -> AgentState:
    """Retrieves context from the vector store."""
    logger.info("Executing node: retrieve_node")
    retriever = Retriever(state["session_id"])
    chunks = retriever.retrieve(state["user_query"])
    
    state["retrieved_chunks"] = chunks
    
    if chunks:
        avg_score = sum(c["score"] for c in chunks) / len(chunks)
        state["confidence_score"] = avg_score
    else:
        state["confidence_score"] = 0.0
    
    # Build context string
    context_parts = []
    sources = []
    for c in chunks:
        context_parts.append(f"[Source: {c['metadata']['source']}, Page: {c['metadata']['page_number']}]\n{c['text']}")
        sources.append({"source": c['metadata']['source'], "page": c['metadata']['page_number']})
        
    state["context_string"] = "\n\n".join(context_parts) if context_parts else "No relevant documents found."
    
    # Deduplicate sources
    unique_sources = []
    for s in sources:
        if s not in unique_sources:
            unique_sources.append(s)
            
    state["sources"] = unique_sources
    return state

def analyze_query_node(state: AgentState) -> AgentState:
    """Analyzes query against context to decide the route."""
    logger.info("Executing node: analyze_query_node")
    
    if not state.get("retrieved_chunks"):
        state["route"] = "fallback"
        state["routing_reason"] = "No relevant context retrieved."
        logger.info("No chunks retrieved. Bypassing LLM and defaulting to fallback.")
        return state
        
    llm = LLMGenerator()
    analysis = llm.analyze_query(state["user_query"], state["context_string"])
    
    state["route"] = analysis.get("route", "fallback")
    state["routing_reason"] = analysis.get("reason", "Unknown")
    logger.info(f"Route determined: {state['route']} - Reason: {state['routing_reason']}")
    return state

def generate_answer_node(state: AgentState) -> AgentState:
    """Generates the final answer using retrieved context."""
    logger.info("Executing node: generate_answer_node")
    llm = LLMGenerator()
    answer = llm.generate_answer(state["user_query"], state["context_string"])
    state["final_response"] = answer
    return state

def clarify_node(state: AgentState) -> AgentState:
    """Handles vague queries by asking for clarification."""
    logger.info("Executing node: clarify_node")
    state["final_response"] = "Could you please provide more specific details or clarify your question? I want to make sure I give you the most accurate answer from the documents."
    return state

def fallback_node(state: AgentState) -> AgentState:
    """Handles cases where context is missing."""
    logger.info("Executing node: fallback_node")
    state["final_response"] = "I'm sorry, but I cannot find the answer to your question in the uploaded documents."
    return state

def escalate_node(state: AgentState) -> AgentState:
    """Handles escalation to a human agent."""
    logger.info("Executing node: escalate_node")
    state["escalation_required"] = True
    
    ticket = EscalationManager.create_ticket(
        session_id=state["session_id"],
        query=state["user_query"],
        history=state["context_string"][:500] + "... (truncated)", # just a snippet for history
        reason=state["routing_reason"]
    )
    state["escalation_ticket"] = ticket
    state["final_response"] = "This query requires human review. Escalating to an agent..."
    return state
