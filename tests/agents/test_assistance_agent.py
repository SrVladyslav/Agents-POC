"""Tests for AssistanceAgent._build_action: validation/normalization of
the parsed data and the decision of whether to trigger an
AssistanceRequestAction.
"""

from src.actions.assistance_request_action import AssistanceRequestAction
from src.agents.assistance_agent import AssistanceAgent
from src.integrations.http import SimulatedHttpClient


def _build_agent() -> AssistanceAgent:
    return AssistanceAgent(
        conversation_model=None,  # not used by _build_action directly
        parser_model=None,
        http_client=SimulatedHttpClient(),
    )


def test_build_action_returns_action_when_request_is_present():
    agent = _build_agent()
    raw_data = {"request": "I want to change my billing address"}

    action = agent._build_action(raw_data)

    assert isinstance(action, AssistanceRequestAction)
    assert action.payload == {"request": "I want to change my billing address"}


def test_build_action_returns_none_when_request_is_none():
    agent = _build_agent()

    assert agent._build_action({"request": None}) is None


def test_build_action_returns_none_when_request_is_missing():
    agent = _build_agent()

    assert agent._build_action({}) is None


def test_build_action_returns_none_when_request_is_empty_string():
    agent = _build_agent()

    assert agent._build_action({"request": ""}) is None
