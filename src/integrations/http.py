from src.protocols.http_client import HttpClient
import httpx


class SimulatedHttpClient(HttpClient):
    """
    Simulated HTTPClient simulation

    Constructs a real HTTP request (using httpx.Request) which validates
    the URL, headers, and body serialization, but never sends the request.

    It assumes that the request is successful and returns a response 200 OK.
    """

    def post(
        self, url: str, headers: dict[str, str], body: dict[str, str]
    ) -> httpx.Response:
        # httpx.request vaidates the URL, Normalizes the headers and serialzies the
        # body to JON the same way as the API expects it.
        request = httpx.Request("POST", url=url, headers=headers, json=body)

        print(f"[SIMULATED HTTP CLIENT] {request.method} {request.url}")
        print(f"  headers: {dict(request.headers)}")
        print(f"  body: {request.content.decode()}")

        # Nothing is sent over the internet, we assume that the response is 200 OK
        return httpx.Response(status_code=200, json={"status": "ok"})
