from src.simulation.conversation_state import ConversationState


class SimulatedAssistanceParserModel(ConversationState):

    def parse_data(self) -> dict[str, str]:
        return {"request": "I want to change my billing address"}
