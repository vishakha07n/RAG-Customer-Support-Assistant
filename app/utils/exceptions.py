class RAGException(Exception):
    """Base exception for RAG application"""
    pass

class IngestionError(RAGException):
    """Raised when document ingestion fails"""
    pass

class VectorStoreError(RAGException):
    """Raised when vector store operations fail"""
    pass

class LLMGenerationError(RAGException):
    """Raised when LLM generation fails"""
    pass
