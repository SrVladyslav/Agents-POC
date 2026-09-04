"""Smoke/integration test for the completed main(): it should wire up
both agents with their simulated models and run one full turn each,
without raising, printing the response of both turns.
"""

from src.main import main


def test_main_runs_both_agents_turns_without_errors(capsys):
    main()

    captured = capsys.readouterr()

    assert "DebtAgent turn" in captured.out
    assert "AssistanceAgent turn" in captured.out
    # The response returned by the (simulated) DebtAgent conversation turn.
    assert "500 EUR" in captured.out
    # The response returned by the (simulated) AssistanceAgent conversation turn.
    assert "billing address" in captured.out
