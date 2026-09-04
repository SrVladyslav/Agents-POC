from abc import ABC, abstractmethod

from src.config import secrets
from src.protocols.http_client import HttpClient


class BaseAction(ABC):
    """Base class for all actions that can be performed by the agent."""

    # This payload is used for deduplication purposes and store the actual paylod
    payload: dict[str, str | bool | float | int]

    def __init__(self, parsed_data: dict[str, str]):
        self.payload = parsed_data

    def _build_headers(self, parsed_data: dict[str, str]) -> dict[str, str]:
        """Builds the headers for the HTTP request.

        Every call is assumed to require Bearer Token authentication, plus
        any other non-None field returned by the ParserModel, stringified.

        Args:
            parsed_data (dict[str, str]): Parsed data whose non-None values
                are added as extra headers.

        Returns:
            dict[str, str]: Headers including the Authorization bearer token.
        """

        return {
            "Authorization": f"Bearer {secrets.API_TOKEN}",
            **{
                key: str(value)
                for key, value in parsed_data.items()
                if value is not None
            },  # Force all the values to be strings
        }

    @abstractmethod
    def execute(self, http_client: HttpClient) -> None:
        """Sends the action's request to its target API.

        Args:
            http_client (HttpClient): Client used to perform the HTTP call.
        """
        ...
