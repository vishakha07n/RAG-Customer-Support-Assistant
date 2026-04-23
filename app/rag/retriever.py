from typing import List, Dict, Any, Tuple
from app.rag.vector_store import VectorStore
from app.config import settings
from app.utils.logger import get_logger
import os

logger = get_logger(__name__)

class Retriever:
    def __init__(self, session_id: str):
        self.vector_store = VectorStore(session_id)

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """
        Retrieves top-k similar chunks for a given query from the session's collection.
        Filters by similarity threshold.
        """
        # Removed os.path.exists check to prevent false early returns.

        vs = self.vector_store._get_vectorstore()
        
        # FIX 2: Force verify vector DB content
        try:
            collection_count = vs._collection.count()
            logger.info(f"[DEBUG] VectorDB Collection Count before query: {collection_count}")
        except Exception as e:
            logger.error(f"[DEBUG] Failed to get collection count: {e}")
            
        # Chroma default is L2 distance, smaller distance = higher similarity
        results = vs.similarity_search_with_score(
            query, 
            k=settings.RETRIEVER_K
        )
        
        # FIX 1: Debug retrieval output
        logger.info(f"[DEBUG] Raw retrieved docs count: {len(results)}")
        for i, (doc, distance) in enumerate(results):
            logger.info(f"[DEBUG] Doc {i} Distance: {distance} | Content Snippet: {doc.page_content[:100]}...")
        
        filtered_results = []
        for doc, distance in results:
            # Convert L2 distance to a basic confidence score (0 to 1)
            # If distance is 0, confidence is 1. As distance grows, confidence drops.
            confidence = 1.0 / (1.0 + float(distance))
            
            # Use a much more forgiving threshold to drop complete noise
            # User config SIMILARITY_THRESHOLD can be used here or we default to a low value
            if confidence >= 0.1:  
                filtered_results.append({
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": confidence
                })
                
        logger.info(f"Retrieved {len(filtered_results)} chunks for query with confidence >= 0.1")
        if not filtered_results:
            logger.warning("[DEBUG] ALL retrieved documents were filtered out by the confidence threshold!")
        return filtered_results
print("TEST DEBUG WORKS")

