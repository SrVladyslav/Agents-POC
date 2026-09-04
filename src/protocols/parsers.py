from typing import Protocol


class ParserModel(Protocol):
    """Interface for the parser model, which should expose the
    parse_data function.
    """

    def parse_data(self) -> dict[str, str]:
        """Parses the chat history data and returns it as a JSON-like
        dictionary. The ParserModel is assumed to already have access
        to the conversation history.
        """
        ...
