import httpx

from src.protocols.http_client import HttpClient


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

        print(f"[SIMULATED HTTP CLIENT] {request.method} {request.url}")
        print(f"  headers: {dict(request.headers)}")
        print(f"  body: {request.content.decode()}")

        # Nothing is sent over the internet, we assume that the response is 200 OK
        return httpx.Response(status_code=200, json={"status": "ok"})
