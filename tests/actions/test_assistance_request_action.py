"""Tests for AssistanceRequestAction: it should POST the request payload
to the assistance request endpoint with correctly built headers.
"""

from src.actions.assistance_request_action import AssistanceRequestAction
from tests.conftest import (
    TEST_API_TOKEN,
    TEST_REQUESTS_API_ENDPOINT,
    RecordingHttpClient,
)


def test_execute_posts_request_payload_to_assistance_endpoint(
    recording_http_client: RecordingHttpClient,
):
    payload = {"request": "I want to change my billing address"}
    action = AssistanceRequestAction(payload)

    action.execute(recording_http_client)

    assert len(recording_http_client.calls) == 1
    call = recording_http_client.calls[0]
    assert call["url"] == TEST_REQUESTS_API_ENDPOINT
    assert call["headers"]["Authorization"] == f"Bearer {TEST_API_TOKEN}"
    assert call["headers"]["request"] == "I want to change my billing address"
    assert call["body"] == payload
