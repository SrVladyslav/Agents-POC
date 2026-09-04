from src.agents.assistance_agent import AssistanceAgent
from src.agents.debt_agent import DebtAgent
from src.config import configure_logging
from src.integrations.http import SimulatedHttpClient
from src.simulation.simulated_assistance_parser_model import (
    SimulatedAssistanceParserModel,
)
from src.simulation.simulated_conversation_model import SimulatedConversationModel
from src.simulation.simulated_debt_parser_model import SimulatedDebtParserModel


def main() -> None:
    """Runs one conversation turn for each agent, using simulated models
    and a simulated HTTP client, as a demo of the full turn lifecycle.
    """
    configure_logging()

    http_client = SimulatedHttpClient()

    debt_chat_id = "debt-demo-chat"
    debt_last_message = "Sure, I can pay 500 EUR on 2026-09-15."
    debt_agent = DebtAgent(
        conversation_model=SimulatedConversationModel(
            chat_id=debt_chat_id, history=[], last_user_message=debt_last_message
        ),
        parser_model=SimulatedDebtParserModel(
            chat_id=debt_chat_id, history=[], last_user_message=debt_last_message
        ),
        http_client=http_client,
    )

    assistance_chat_id = "assistance-demo-chat"
    assistance_last_message = "I want to change my billing address."
    assistance_agent = AssistanceAgent(
        conversation_model=SimulatedConversationModel(
            chat_id=assistance_chat_id,
            history=[],
            last_user_message=assistance_last_message,
        ),
        parser_model=SimulatedAssistanceParserModel(
            chat_id=assistance_chat_id,
            history=[],
            last_user_message=assistance_last_message,
        ),
        http_client=http_client,
    )

    print("=== DebtAgent turn ===")
    print(debt_agent.handle_turn())

    print("\n=== AssistanceAgent turn ===")
    print(assistance_agent.handle_turn())


if __name__ == "__main__":
    main()
