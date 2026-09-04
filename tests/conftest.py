"""Shared fixtures and test doubles used across the test suite."""

import httpx
import pytest

from src.config import secrets

TEST_API_TOKEN = "test-token"
TEST_COMMITMENT_API_ENDPOINT = "https://api.ringr.debt/v1/commitment"
TEST_REQUESTS_API_ENDPOINT = "https://api.ringr.assistance/v1/request"


@pytest.fixture(autouse=True)
def stub_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensures no test depends on the real values loaded from
    secrets/.env.<environment>, which are environment-specific and may
    change independently of the test suite.
    """
    monkeypatch.setattr(secrets, "API_TOKEN", TEST_API_TOKEN, raising=False)
    monkeypatch.setattr(
        secrets, "COMMITMENT_API_ENDPOINT", TEST_COMMITMENT_API_ENDPOINT, raising=False
    )
    monkeypatch.setattr(
        secrets, "REQUESTS_API_ENDPOINT", TEST_REQUESTS_API_ENDPOINT, raising=False
    )


class FakeConversationModel:
    """Minimal ConversationModel double returning a fixed response."""

    def __init__(self, response: str = "fake response") -> None:
        self._response = response

    def answer_user(self) -> str:
        return self._response


class FakeParserModel:
    """Minimal ParserModel double returning fixed parsed data.

    The returned dict can be swapped between turns via `set_data`
    to simulate the conversation evolving.
    """

    def __init__(self, data: dict) -> None:
        self._data = data

    def set_data(self, data: dict) -> None:
        self._data = data

    def parse_data(self) -> dict:
        return self._data


class RecordingHttpClient:
    """HttpClient double that records every call instead of sending it,
    so tests can assert on what would have been sent.
    """

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def post(self, url: str, headers: dict, body: dict) -> httpx.Response:
        self.calls.append({"url": url, "headers": headers, "body": body})
        return httpx.Response(status_code=200, json={"status": "ok"})


@pytest.fixture
def recording_http_client() -> RecordingHttpClient:
    return RecordingHttpClient()
