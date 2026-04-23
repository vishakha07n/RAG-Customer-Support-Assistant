from typing import List, Dict, Any
from langchain_community.vectorstores import Chroma
from app.rag.embeddings import get_embedding_model
from app.config import settings
from app.utils.logger import get_logger
from app.utils.helpers import sanitize_collection_name
import shutil
import os

logger = get_logger(__name__)

class VectorStore:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.collection_name = sanitize_collection_name(f"session_{session_id}")
        self.embedding_model = get_embedding_model()
        self.persist_directory = os.path.join(settings.CHROMA_DB_DIR, self.collection_name)
        
    def _get_vectorstore(self) -> Chroma:
        return Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embedding_model,
            persist_directory=self.persist_directory
        )

    def store_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Stores chunks in the session-specific Chroma collection.
        Avoids duplicates based on chunk_id.
        """
        if not chunks:
            logger.warning("No chunks to store.")
            return

        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        ids = [chunk["metadata"]["chunk_id"] for chunk in chunks]

        vectorstore = self._get_vectorstore()
        
        # Check existing chunks to avoid duplicates
        existing_data = vectorstore.get()
        existing_ids = set(existing_data.get("ids", []))
        
        new_texts = []
        new_metadatas = []
        new_ids = []
        
        for text, meta, chunk_id in zip(texts, metadatas, ids):
            if chunk_id not in existing_ids:
                new_texts.append(text)
                new_metadatas.append(meta)
                new_ids.append(chunk_id)
                
        if new_texts:
            logger.info(f"Adding {len(new_texts)} new chunks to collection {self.collection_name}")
            vectorstore.add_texts(texts=new_texts, metadatas=new_metadatas, ids=new_ids)
            vectorstore.persist()
        else:
            logger.info("All chunks already exist in the vector store. Skipping insertion.")

    def clear_collection(self):
        """Removes the session's vector store completely."""
        logger.info(f"Clearing collection {self.collection_name}")
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)
            logger.info("Collection cleared successfully.")



