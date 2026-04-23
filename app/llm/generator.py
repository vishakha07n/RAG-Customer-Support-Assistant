import json
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from app.config import settings
from app.utils.logger import get_logger
from app.utils.exceptions import LLMGenerationError
from app.llm.prompts import QA_SYSTEM_PROMPT, ROUTING_PROMPT

logger = get_logger(__name__)

class LLMGenerator:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set. LLM generation may fail if not properly configured.")
        self.llm = ChatGroq(
            model=settings.LLM_MODEL_NAME,
            temperature=0.0,
            groq_api_key=settings.GROQ_API_KEY or "dummy_key_for_local"
        )

    def _invoke_with_fallback(self, messages):
        """Helper to invoke LLM with a fallback if the primary model is decommissioned."""
        try:
            return self.llm.invoke(messages)
        except Exception as e:
            error_str = str(e).lower()
            if "decommissioned" in error_str or "not_found" in error_str or "invalid_request_error" in error_str:
                fallback_model = "llama-3.1-8b-instant"
                logger.error(f"Model {settings.LLM_MODEL_NAME} failed (likely decommissioned). Falling back to {fallback_model}. Error details: {e}")
                
                fallback_llm = ChatGroq(
                    model=fallback_model,
                    temperature=0.0,
                    groq_api_key=settings.GROQ_API_KEY or "dummy_key_for_local"
                )
                return fallback_llm.invoke(messages)
            # Re-raise if it's a different error
            raise e

    def analyze_query(self, query: str, context: str) -> dict:
        """
        Analyzes the query and context to determine the route.
        Returns a dict with 'route' and 'reason'.
        """
        system_msg = SystemMessage(content="You are a routing assistant. Only return valid JSON.")
        prompt_text = ROUTING_PROMPT.format(query=query, context=context)
        human_msg = HumanMessage(content=prompt_text)
        
        try:
            response = self._invoke_with_fallback([system_msg, human_msg])
            content = response.content.strip()
            
            # Robust JSON extraction
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1:
                content = content[start:end+1]
                return json.loads(content)
            else:
                logger.warning(f"Could not find JSON object in LLM response: {content}")
                return {"route": "answer", "reason": "Failed to parse JSON, defaulting to answer."}
                
        except Exception as e:
            logger.error(f"Failed to analyze query: {e}. Raw response: {response.content if 'response' in locals() else 'None'}")
            return {"route": "answer", "reason": "Routing analysis failed, defaulting to answer."}

    def generate_answer(self, query: str, context: str) -> str:
        """
        Generates an answer based STRICTLY on context.
        """
        system_msg = SystemMessage(content=QA_SYSTEM_PROMPT.format(context=context))
        human_msg = HumanMessage(content=query)
        
        try:
            response = self._invoke_with_fallback([system_msg, human_msg])
            return response.content
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            raise LLMGenerationError(f"LLM generation failed: {e}")
