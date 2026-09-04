import logging

import httpx

from src.protocols.http_client import HttpClient

logger = logging.getLogger(__name__)


class SimulatedHttpClient(HttpClient):
    """Simulated HttpClient implementation.

    Constructs a real HTTP request (using httpx.Request) which validates
    the URL, headers, and body serialization, but never sends the request.

    It assumes that the request is successful and returns a response 200 OK.
    """

    def post(
        self, url: str, headers: dict[str, str], body: dict[str, str]
    ) -> httpx.Response:
        """Builds and logs a POST request without sending it over the network.

        Args:
            url (str): Target endpoint URL.
            headers (dict[str, str]): Request headers.
            body (dict[str, str]): Request body, serialized to JSON.

        Returns:
            httpx.Response: A simulated 200 OK response.
        """
        # httpx.Request validates the URL, normalizes the headers, and serializes the
        # body to JSON the same way as the API expects it.
        request = httpx.Request("POST", url=url, headers=headers, json=body)

        logger.info("[SIMULATED HTTP CLIENT] %s %s", request.method, request.url)
        logger.debug("  headers: %s", dict(request.headers))
        logger.debug("  body: %s", request.content.decode())

        # Nothing is sent over the internet, we assume that the response is 200 OK
        return httpx.Response(status_code=200, json={"status": "ok"})
