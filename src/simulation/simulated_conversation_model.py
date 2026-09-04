from src.simulation.conversation_state import ConversationState


class SimulatedConversationModel(ConversationState):
    """
    This mocks the ConversationModel which is used in the agents.

    In prod we would connect to the llm and load the conversation history,
    so this class should also be able to load the model and history
    with something like:

        def __init__(self, llm, history):
            self.history = history
            self.llm = llm

    Or better, we would use Lanchchain of LlamaIndex to use their implementations.
    """

    def answer_user(self) -> str:
        """Simulates the answer_user function.

        In production this would be a call to the selected LLM
        with the history of the conversation, updating the state, e.g.:

            messages = [
                * history,
                langchain_core.messages.HumanMessage(content=user_input)
            ]

            response = self.llm.invoke(smessages)

            self.history.append(langchain_core.messages.HumanMessage(content=user_input))
            self.history.append(langchain_core.messages.AIMessage(content=response.content))

        Here is just a hardcoded implementation.
        """
        return self.last_user_message
