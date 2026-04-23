import os
from typing import List
from app.graph.builder import build_graph
from app.graph.state import AgentState
from app.rag.pdf_ingestor import PDFIngestor
from app.rag.chunker import Chunker
from app.rag.vector_store import VectorStore
from app.utils.helpers import generate_session_id

class SupportAssistant:
    def __init__(self, session_id: str = None):
        self.session_id = session_id or generate_session_id()
        self.graph = build_graph()
        self.vector_store = VectorStore(self.session_id)

    def process_pdfs(self, file_paths: List[str]):
        all_chunks = []
        ingestor = PDFIngestor()
        chunker = Chunker()

        for path in file_paths:
            pages = ingestor.extract_text_from_pdf(path, self.session_id)
            chunks = chunker.chunk_documents(pages)
            all_chunks.extend(chunks)

        if all_chunks:
            self.vector_store.store_chunks(all_chunks)

    def ask(self, query: str) -> AgentState:
        initial_state: AgentState = {
            "session_id": self.session_id,
            "user_query": query,
            "retrieved_chunks": [],
            "context_string": "",
            "route": "",
            "routing_reason": "",
            "answer_draft": "",
            "escalation_required": False,
            "escalation_ticket": None,
            "human_decision": None,
            "human_custom_reply": None,
            "final_response": "",
            "sources": [],
            "error": None
        }
        return self.graph.invoke(initial_state)

    def reset_session(self):
        self.vector_store.clear_collection()

