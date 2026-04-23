class ReviewerSimulator:
    """
    Simulates a human reviewer for the HITL flow.
    In a real app, this would be a separate dashboard.
    """
    @staticmethod
    def process_decision(decision: str, custom_response: str = "") -> str:
        """
        Processes the human decision.
        Decisions: "approve", "reject", "custom_reply"
        """
        if decision == "approve":
            return "Human agent approved the escalation. We will contact you shortly."
        elif decision == "reject":
            return "Human agent reviewed your request but determined it does not require escalation."
        elif decision == "custom_reply":
            return f"Human Agent Reply: {custom_response}"
        return "Unknown decision."
