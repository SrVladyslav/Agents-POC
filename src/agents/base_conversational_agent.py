from abc import ABC, abstractmethod
from src.protocols.conversations import ConversationModel
from src.protocols.parsers import ParserModel
from src.actions.base_action import BaseAction
from src.protocols.http_client import HttpClient


class BaseConversationalAgent(ABC):
    """
    Base class for all agents which contains all the basic functionality requirements.

    NOTE: We suppose that ConversationModel already handles and contains all the system state
    for the given conversation. It handles things like the current chat ID, the last user message
    and the history of the conversation. When user types a message, something external will
    add it to the conversation history of this ConversationModel object.

    NOTE: We suppose that ParserModel already has access to the conversation history internally,
    so we don't need to pass extra parameters to the parse_data function.
    """

    def __init__(
        self,
        conversation_model: ConversationModel,
        parser_model: ParserModel,
        http_client: HttpClient,
    ):
        self._conversation_model = conversation_model
        self._parser_model = parser_model
        self._http_client = http_client

        # This is used to keep track of the last action sent in this conversations
        # and to avoid duplicated actions
        self._sent_payloads: set[frozenset] = set()

    def handle_turn(self) -> str:
        """
        Reprsents an execution turn of the agent.
        """
        # Obtain the response from the ConversationModel object
        # NOTE: answer_user() can get the last user msg from the history and call the LLM
        response: str = self._conversation_model.answer_user()

        # Parse the relevant information from the response with ParseModel
        # NOTE: We suppose that parse_data() has access to the conversation history
        # and it returns the current structured state of the conversation
        raw_data: dict[str, str] = self._parser_model.parse_data()

        # Validate and normalize the parsed reponse,check if the agent has any action to perform
        # NOTE: We don't execute internally since we want to check for dedups
        action: BaseAction | None = self._build_action(raw_data)

        # Execute the respective action with the HTTP simulated request if needed
        if action is not None:
            dedupe_key: frozenset = frozenset(action.payload.items())

            if dedupe_key not in self._sent_payloads:
                # Makes the request to the respective API Endpoint
                action.execute(self._http_client)

                # Update the last sent actions in order to avoid duplicated actions
                self._sent_payloads.add(dedupe_key)

        return response

    @abstractmethod
    def _build_action(self, raw_data: dict[str, str]) -> BaseAction | None:
        """Given the raw data, validates it and normalizes for every action,
        checks if some action should be executed, if so, creates it and returns it.

        Args:
            validated_data (dict[str, str]): Validated data to be used for building the action if should be executed.

        Returns:
            BaseAction | None: Action to be executed if any or None if no action is required.
        """
        ...
