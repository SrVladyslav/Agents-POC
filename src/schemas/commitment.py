from pydantic import BaseModel


class CommitmentData(BaseModel):
    commitment_date: str | None = None
    committed_amount: float | None = None
