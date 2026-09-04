"""Tests for BaseAction, focused on the shared header-building logic
(Bearer auth + parsed-data-as-headers) reused by every concrete action.
"""

from src.actions.base_action import BaseAction
from src.protocols.http_client import HttpClient
from tests.conftest import TEST_API_TOKEN


class _ConcreteAction(BaseAction):
    """Minimal concrete subclass, since BaseAction is abstract."""

    def execute(self, http_client: HttpClient) -> None:
        pass


def test_build_headers_includes_bearer_token_from_secrets():
    action = _ConcreteAction({})

    headers = action._build_headers({})

    assert headers["Authorization"] == f"Bearer {TEST_API_TOKEN}"


def test_build_headers_merges_parsed_data_as_stringified_headers():
    action = _ConcreteAction({})
    parsed_data = {"commitment_date": "2026-09-15", "committed_amount": 500.0}

    headers = action._build_headers(parsed_data)

    assert headers["commitment_date"] == "2026-09-15"
    assert headers["committed_amount"] == "500.0"


def test_build_headers_excludes_none_values():
    action = _ConcreteAction({})
    parsed_data = {"request": None, "commitment_date": "2026-09-15"}

    headers = action._build_headers(parsed_data)

    assert "request" not in headers
    assert headers["commitment_date"] == "2026-09-15"
