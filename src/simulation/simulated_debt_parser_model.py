from src.simulation.conversation_state import ConversationState


class SimulatedDebtParserModel(ConversationState):

    def parse_data(self) -> dict[str, str]:
        return {
            "commitment_date": "2026-09-15",
            "committed_amount": "500.0",
        }
