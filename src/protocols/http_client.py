from typing import Protocol

from httpx import Response


class HttpClient(Protocol):
    """Interface for the HTTP client used to perform outgoing API calls."""

    def post(
        self, url: str, headers: dict[str, str], body: dict[str, str]
    ) -> Response:
        """Sends a POST request.

        Args:
            url (str): Target endpoint URL.
            headers (dict[str, str]): Request headers.
            body (dict[str, str]): Request body, serialized to JSON.

        Returns:
            Response: The HTTP response.
        """
        ...
