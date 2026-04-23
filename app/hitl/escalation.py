import datetime
import json
from typing import Dict, Any

class EscalationManager:
    @staticmethod
    def create_ticket(session_id: str, query: str, history: str, reason: str) -> Dict[str, Any]:
        """
        Creates an escalation ticket payload in memory.
        """
        ticket = {
            "ticket_id": f"TKT-{session_id[:8]}-{int(datetime.datetime.now().timestamp())}",
            "session_id": session_id,
            "status": "pending_review",
            "timestamp": datetime.datetime.now().isoformat(),
            "user_query": query,
            "escalation_reason": reason,
            "context_history": history
        }
        return ticket

    @staticmethod
    def format_ticket_for_ui(ticket: Dict[str, Any]) -> str:
        return json.dumps(ticket, indent=2)
