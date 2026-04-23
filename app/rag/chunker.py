from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class Chunker:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )

    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Splits extracted pages into smaller chunks while preserving metadata.
        """
        logger.info(f"Chunking {len(documents)} documents...")
        chunks = []
        
        for doc in documents:
            text = doc["text"]
            base_metadata = doc["metadata"]
            
            split_texts = self.text_splitter.split_text(text)
            
            for i, chunk_text in enumerate(split_texts):
                chunk_metadata = base_metadata.copy()
                chunk_metadata["chunk_id"] = f"{base_metadata['source']}_p{base_metadata['page_number']}_c{i}"
                chunks.append({"text": chunk_text, "metadata": chunk_metadata})
                
        logger.info(f"Created {len(chunks)} total chunks.")
        return chunks
