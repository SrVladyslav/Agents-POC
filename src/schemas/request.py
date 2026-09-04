from pydantic import BaseModel


class RequestData(BaseModel):
    """The user's doubt or request, to be registered for a human agent."""

    request: str | None = None
