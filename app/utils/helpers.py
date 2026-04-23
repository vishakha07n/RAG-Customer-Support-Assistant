import uuid
import re

def generate_session_id() -> str:
    """Generates a unique, URL-safe session ID."""
    return str(uuid.uuid4())

def sanitize_collection_name(name: str) -> str:
    """
    Sanitizes string to be a valid ChromaDB collection name.
    ChromaDB requires: 3-63 chars, starts/ends with alphanumeric, only alphanumeric/underscores/hyphens.
    """
    clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    # Ensure it doesn't start or end with non-alphanumeric
    clean_name = clean_name.strip('_-')
    if len(clean_name) < 3:
        clean_name = clean_name.ljust(3, '0')
    if len(clean_name) > 63:
        clean_name = clean_name[:63]
    return clean_name
