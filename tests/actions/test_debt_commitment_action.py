"""Tests for DebtCommitmentAction: it should POST the commitment payload
to the debt commitment endpoint with correctly built headers.
"""

from src.actions.debt_commitment_action import DebtCommitmentAction
from tests.conftest import (
    TEST_API_TOKEN,
    TEST_COMMITMENT_API_ENDPOINT,
    RecordingHttpClient,
)


def test_execute_posts_commitment_payload_to_commitment_endpoint(
    recording_http_client: RecordingHttpClient,
):
    payload = {"commitment_date": "2026-09-15", "committed_amount": "500.0"}
    action = DebtCommitmentAction(payload)

    action.execute(recording_http_client)

    assert len(recording_http_client.calls) == 1
    call = recording_http_client.calls[0]
    assert call["url"] == TEST_COMMITMENT_API_ENDPOINT
    assert call["headers"]["Authorization"] == f"Bearer {TEST_API_TOKEN}"
    assert call["headers"]["commitment_date"] == "2026-09-15"
    assert call["headers"]["committed_amount"] == "500.0"
    assert call["body"] == payload
