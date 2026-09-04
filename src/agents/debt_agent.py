from pydantic import ValidationError

from src.actions.base_action import BaseAction
from src.actions.debt_commitment_action import DebtCommitmentAction
from src.agents.base_conversational_agent import BaseConversationalAgent
from src.schemas.commitment import CommitmentData


class DebtAgent(BaseConversationalAgent):
    """
    The mission is to register the pending debts.

    The information it needs to parse from the conversation is:
    - Commitment date: commitment_date: str | None in format yyyy-mm-dd
    - Committed amount: commitment_amount: float | None

    Then, in case they are not None, register the debt by calling the POST API https://api.ringr.debt/v1/commitment
    """

    def _build_action(self, raw_data: dict[str, str]) -> BaseAction | None:
        """Given the raw data, validates it as commitment data and, if both
        the commitment date and amount are present, builds the action that
        registers the debt.

        Args:
            raw_data (dict[str, str]): Parsed data to be validated and normalized.

        Returns:
            BaseAction | None: Action to be executed if any or None if no action is required.
        """
        try:
            data = CommitmentData.model_validate(raw_data)
        except ValidationError:
            return None

        # In order to proceed with the API call, commitment and committed_amount is needed
        if data.commitment_date is None or data.committed_amount is None:
            return None

        return DebtCommitmentAction(data.model_dump(mode="json", exclude_none=True))
