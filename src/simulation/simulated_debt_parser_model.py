from src.simulation.conversation_state import ConversationState


class SimulatedDebtParserModel(ConversationState):
    """Simulated ParserModel for the debt flow: always returns the same
    hardcoded commitment data instead of parsing it from the conversation.
    """

    def parse_data(self) -> dict[str, str]:
        """Returns a fixed, hardcoded debt commitment."""
        return {
            "commitment_date": "2026-09-15",
            "committed_amount": "500.0",
        }
