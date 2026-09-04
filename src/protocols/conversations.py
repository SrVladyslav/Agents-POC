from typing import Protocol


class ConversationModel(Protocol):
    """This is just an interface for the conversational model,
    which should expose the answer_user function."""

    def answer_user(self) -> str: ...
