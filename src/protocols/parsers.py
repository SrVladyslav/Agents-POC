from typing import Protocol


class ParserModel(Protocol):
    def parse_data(self) -> dict[str, str]:
        """
        Parses the chat history data and returns
        it as a JSON-like ditionary. We suppose that the ParserModel
        has already access to the conversation history.
        """
        ...
