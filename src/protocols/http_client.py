from typing import Protocol

from httpx import Response


class HttpClient(Protocol):
    def post(
        self, url: str, headers: dict[str, str], body: dict[str, str]
    ) -> Response: ...
