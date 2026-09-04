from src.simulation.conversation_state import ConversationState


class SimulatedAssistanceParserModel(ConversationState):
    """Simulated ParserModel for the assistance flow: always returns the
    same hardcoded request instead of parsing it from the conversation.
    """

    def parse_data(self) -> dict[str, str]:
        """Returns a fixed, hardcoded assistance request."""
        return {"request": "I want to change my billing address"}
