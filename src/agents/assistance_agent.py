from src.agents.base_conversational_agent import BaseConversationalAgent
from src.actions.base_action import BaseAction
from src.schemas.request import RequestData
from src.actions.assistance_request_action import AssistanceRequestAction
from pydantic import ValidationError


class AssistanceAgent(BaseConversationalAgent):
    """
    The mission is to resolve the doubts of the user and register petitions to be processed by human agents.

    The information it needs to parse from the conversation is:
    - The user's doubt: request: str | None
    - If the user has a doubt, then we need to register it by calling the POST API at https://api.ringr.assistance/v1/request
    """

    def _build_action(self, raw_data: dict[str, str]) -> BaseAction | None:
        """Given the raw data, validates it and normalizes for every action,
        checks if some action should be executed, if so, creates it and returns it.

        Args:
            raw_data (dict[str, str]): Parsed data to be validated and normalized.

        Returns:
            BaseAction | None: Action to be executed if any or None if no action is required.
        """
        try:
            data: RequestData = RequestData.model_validate(raw_data)
        except ValidationError:
            return None

        # In order to procees with the API call, we need to have the request field
        if not data.request:
            return None

        return AssistanceRequestAction(data.model_dump(mode="json", exclude_none=True))
