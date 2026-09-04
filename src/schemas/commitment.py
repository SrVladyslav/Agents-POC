from datetime import date

from pydantic import BaseModel


class CommitmentData(BaseModel):
    """Debt commitment fields parsed from the conversation.

    Both fields must be present (non-None) for a debt commitment action
    to be registered.
    """

    commitment_date: date | None = None  # Validated as yyyy-mm-dd
    committed_amount: float | None = None
