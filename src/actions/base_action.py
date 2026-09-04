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

        NOTE: We suppose that ALL the calls should have the Bearer Token authentication,
        as well as consider as headers all the other data that is returned by the ParserModel.
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
        """Executes the action sending the respective request to the API.

        NOTE: http_client can be deleted, but for extra purposes in the future
        I prefer to keep it as optional too.
        """
        ...
