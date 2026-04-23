import pypdf
from typing import List, Dict, Any
from app.utils.logger import get_logger
from app.utils.exceptions import IngestionError
import os

logger = get_logger(__name__)

class PDFIngestor:
    @staticmethod
    def extract_text_from_pdf(file_path: str, session_id: str) -> List[Dict[str, Any]]:
        """
        Extracts text from a PDF file page by page and attaches metadata.
        """
        if not os.path.exists(file_path):
            raise IngestionError(f"File not found: {file_path}")
            
        filename = os.path.basename(file_path)
        logger.info(f"Extracting text from {filename} for session {session_id}")
        
        extracted_pages = []
        try:
            with open(file_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text = page.extract_text().strip()
                    
                    if text:  # Ignore empty pages
                        metadata = {
                            "source": filename,
                            "page_number": page_num + 1,
                            "session_id": session_id
                        }
                        extracted_pages.append({"text": text, "metadata": metadata})
            
            logger.info(f"Successfully extracted {len(extracted_pages)} pages from {filename}")
            return extracted_pages
            
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {str(e)}")
            raise IngestionError(f"PDF extraction failed: {str(e)}")
