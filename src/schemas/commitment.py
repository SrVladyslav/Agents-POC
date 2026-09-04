import re
from datetime import datetime
from pydantic import BaseModel, field_validator

_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class CommitmentData(BaseModel):
    """Debt commitment fields parsed from the conversation.

    Both fields must be present (non-None) for a debt commitment action
    to be registered.
    """

    commitment_date: str | None = None  # Validated as yyyy-mm-dd
    committed_amount: float | None = None

    @field_validator("commitment_date")
    @classmethod
    def validate_commitment_date(cls, value: str | None) -> str | None:
        """Validates the commitment date as a valid date string in format yyyy-mm-dd."""

        if value is None:
            return None

        # Deny dates as 2030-9-5 (no leading zeroes)
        if not _DATE_PATTERN.match(value):
            raise ValueError(
                f"Invalid commitment date: {value}. Expected format: yyyy-mm-dd"
            )

        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError as exception:
            raise ValueError(
                f"Invalid commitment date: {value}. Expected format: yyyy-mm-dd"
            ) from exception

        return value
