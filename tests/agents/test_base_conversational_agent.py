"""Tests for the handle_turn lifecycle implemented in
BaseConversationalAgent: fetching the response, deciding whether to act,
and deduplicating repeated actions across turns.

DebtAgent is used as a concrete, minimal-effort implementation of the
abstract base class to exercise this shared behavior.
"""

from src.agents.debt_agent import DebtAgent
from tests.conftest import FakeConversationModel, FakeParserModel, RecordingHttpClient

COMMITMENT_DATA = {"commitment_date": "2026-09-15", "committed_amount": 500.0}
OTHER_COMMITMENT_DATA = {"commitment_date": "2026-10-01", "committed_amount": 100.0}
INCOMPLETE_DATA = {"commitment_date": None, "committed_amount": None}


def test_handle_turn_returns_the_conversation_model_response(
    recording_http_client: RecordingHttpClient,
):
    agent = DebtAgent(
        conversation_model=FakeConversationModel("here is my answer"),
        parser_model=FakeParserModel(INCOMPLETE_DATA),
        http_client=recording_http_client,
    )

    assert agent.handle_turn() == "here is my answer"


def test_handle_turn_executes_action_when_conditions_are_met(
    recording_http_client: RecordingHttpClient,
):
    agent = DebtAgent(
        conversation_model=FakeConversationModel(),
        parser_model=FakeParserModel(COMMITMENT_DATA),
        http_client=recording_http_client,
    )

    agent.handle_turn()

    assert len(recording_http_client.calls) == 1


def test_handle_turn_does_not_execute_action_when_conditions_are_not_met(
    recording_http_client: RecordingHttpClient,
):
    agent = DebtAgent(
        conversation_model=FakeConversationModel(),
        parser_model=FakeParserModel(INCOMPLETE_DATA),
        http_client=recording_http_client,
    )

    agent.handle_turn()

    assert recording_http_client.calls == []


def test_handle_turn_does_not_send_duplicate_action_across_turns(
    recording_http_client: RecordingHttpClient,
):
    parser_model = FakeParserModel(COMMITMENT_DATA)
    agent = DebtAgent(
        conversation_model=FakeConversationModel(),
        parser_model=parser_model,
        http_client=recording_http_client,
    )

    agent.handle_turn()
    agent.handle_turn()

    assert len(recording_http_client.calls) == 1


def test_handle_turn_called_twice_with_same_message_deduplicates_the_action(
    recording_http_client: RecordingHttpClient,
):
    """Simulates the same user message being handled across two turns
    (e.g. the conversation state hasn't moved on yet): the parsed data
    stays identical, so the second handle_turn() call must not resend
    the commitment action.
    """
    agent = DebtAgent(
        conversation_model=FakeConversationModel("Sure, I can pay 500 EUR on 2026-09-15."),
        parser_model=FakeParserModel(COMMITMENT_DATA),
        http_client=recording_http_client,
    )

    first_response = agent.handle_turn()
    second_response = agent.handle_turn()

    assert first_response == second_response == "Sure, I can pay 500 EUR on 2026-09-15."
    assert len(recording_http_client.calls) == 1


def test_handle_turn_sends_action_again_when_payload_changes(
    recording_http_client: RecordingHttpClient,
):
    parser_model = FakeParserModel(COMMITMENT_DATA)
    agent = DebtAgent(
        conversation_model=FakeConversationModel(),
        parser_model=parser_model,
        http_client=recording_http_client,
    )

    agent.handle_turn()
    parser_model.set_data(OTHER_COMMITMENT_DATA)
    agent.handle_turn()

    assert len(recording_http_client.calls) == 2
