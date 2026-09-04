import logging

from src.actions.base_action import BaseAction
from src.config import secrets
from src.protocols.http_client import HttpClient

logger = logging.getLogger(__name__)


class DebtCommitmentAction(BaseAction):
    """Registers a user's debt commitment (date and amount), by posting it
    to the debt commitment API.
    """

    def __init__(self, commitment_data: dict[str, str]):
        super().__init__(commitment_data)

    def execute(self, http_client: HttpClient) -> None:
        """Builds the request headers/body from the parsed data and POSTs
        them to `secrets.COMMITMENT_API_ENDPOINT`.

        Args:
            http_client (HttpClient): Client used to perform the HTTP call.
        """
        try:
            http_client.post(
                url=secrets.COMMITMENT_API_ENDPOINT,
                headers=self._build_headers(self.payload),
                body=self.payload,
            )
        except Exception:
            logger.exception(
                "Failed to submit debt commitment to %s",
                secrets.COMMITMENT_API_ENDPOINT,
            )
