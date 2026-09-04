from pydantic import BaseModel


class RequestData(BaseModel):
    request: str | None = None
