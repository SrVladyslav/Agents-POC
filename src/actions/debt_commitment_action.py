from src.actions.base_action import BaseAction
from src.config import secrets
from src.protocols.http_client import HttpClient


class DebtCommitmentAction(BaseAction):
    """Action to commit a debt APi call with all the needed data."""

    def __init__(self, commitment_data: dict[str, str]):
        super().__init__(commitment_data)

    def execute(self, http_client: HttpClient) -> None:
        """Executes the action by sending the request to the respective API."""

        http_client.post(
            url=secrets.COMMITMENT_API_ENDPOINT,
            headers=self._build_headers(self.payload),
            body=self.payload,
        )
