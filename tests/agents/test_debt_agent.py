"""Tests for DebtAgent._build_action: validation/normalization of the
parsed data and the decision of whether to trigger a DebtCommitmentAction.
"""

from src.actions.debt_commitment_action import DebtCommitmentAction
from src.agents.debt_agent import DebtAgent
from src.integrations.http import SimulatedHttpClient


def _build_agent() -> DebtAgent:
    return DebtAgent(
        conversation_model=None,  # not used by _build_action directly
        parser_model=None,
        http_client=SimulatedHttpClient(),
    )


def test_build_action_returns_action_when_both_fields_present():
    agent = _build_agent()
    raw_data = {"commitment_date": "2026-09-15", "committed_amount": 500.0}

    action = agent._build_action(raw_data)

    assert isinstance(action, DebtCommitmentAction)
    assert action.payload == {
        "commitment_date": "2026-09-15",
        "committed_amount": 500.0,
    }


def test_build_action_returns_none_when_commitment_date_is_none():
    agent = _build_agent()
    raw_data = {"commitment_date": None, "committed_amount": 500.0}

    assert agent._build_action(raw_data) is None


def test_build_action_returns_none_when_committed_amount_is_none():
    agent = _build_agent()
    raw_data = {"commitment_date": "2026-09-15", "committed_amount": None}

    assert agent._build_action(raw_data) is None


def test_build_action_returns_none_when_both_fields_are_missing():
    agent = _build_agent()

    assert agent._build_action({}) is None


def test_build_action_returns_none_when_data_is_invalid():
    agent = _build_agent()
    raw_data = {"commitment_date": "2026-09-15", "committed_amount": "not-a-number"}

    assert agent._build_action(raw_data) is None


def test_build_action_returns_none_when_commitment_date_has_wrong_format():
    agent = _build_agent()
    raw_data = {"commitment_date": "15-09-2026", "committed_amount": 500.0}

    assert agent._build_action(raw_data) is None
