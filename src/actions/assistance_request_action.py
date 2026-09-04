import logging

from src.actions.base_action import BaseAction
from src.config import secrets
from src.protocols.http_client import HttpClient

logger = logging.getLogger(__name__)


class AssistanceRequestAction(BaseAction):
    """Registers a user's assistance request for a human agent to process,
    by posting it to the assistance requests API.
    """

    def __init__(self, parsed_data: dict[str, str]):
        super().__init__(parsed_data)

    def execute(self, http_client: HttpClient) -> None:
        """Builds the request headers/body from the parsed data and POSTs
        them to `secrets.REQUESTS_API_ENDPOINT`.

        Args:
            http_client (HttpClient): Client used to perform the HTTP call.
        """
        try:
            http_client.post(
                url=secrets.REQUESTS_API_ENDPOINT,
                headers=self._build_headers(self.payload),
                body=self.payload,
            )
        except Exception:
            logger.exception(
                "Failed to submit assistance request to %s",
                secrets.REQUESTS_API_ENDPOINT,
            )
