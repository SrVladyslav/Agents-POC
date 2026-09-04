from src.actions.base_action import BaseAction
from src.config import secrets
from src.protocols.http_client import HttpClient


class AssistanceRequestAction(BaseAction):
    """Action to request assistance."""

    def __init__(self, parsed_data: dict[str, str]):
        super().__init__(parsed_data)

    def execute(self, http_client: HttpClient) -> None:
        """Executes the action by sending the request to the respective API."""

        http_client.post(
            url=secrets.REQUESTS_API_ENDPOINT,
            headers=self._build_headers(self.payload),
            body=self.payload,
        )
