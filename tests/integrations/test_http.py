"""Tests for SimulatedHttpClient: it must build a real, valid httpx.Request
(so URL/headers/body get real validation and serialization) but never
actually send it, always returning a synthetic 200 OK response.
"""

import httpx
import pytest

from src.integrations.http import SimulatedHttpClient


def test_post_returns_a_simulated_200_ok_response():
    client = SimulatedHttpClient()

    response = client.post(
        url="https://api.ringr.debt/v1/commitment",
        headers={"Authorization": "Bearer test-token"},
        body={"commitment_date": "2026-09-15", "committed_amount": 500.0},
    )

    assert isinstance(response, httpx.Response)
    assert response.status_code == 200


def test_post_validates_the_request_and_raises_on_invalid_header_value():
    """Even though no network call happens, a real httpx.Request is built,
    so an invalid header value (e.g. a non-ASCII string) should still
    raise, proving the validation is real and not skipped.
    """
    client = SimulatedHttpClient()

    with pytest.raises(UnicodeEncodeError):
        client.post(
            url="https://api.ringr.debt/v1/commitment",
            headers={"request": "Dirección inválida"},
            body={},
        )
