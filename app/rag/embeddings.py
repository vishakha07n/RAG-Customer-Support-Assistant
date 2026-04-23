from langchain_community.embeddings import HuggingFaceEmbeddings
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

def get_embedding_model():
    """
    Returns the configured local HuggingFace embedding model.
    """
    logger.info(f"Initializing local HuggingFace Embeddings: {settings.EMBEDDING_MODEL_NAME}")
    return HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL_NAME)
