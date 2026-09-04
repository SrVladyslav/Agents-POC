class ConversationState:
    """This is just a hardcoded conversation state, in prod we should
    connect to some DB and load the history from there.
    """

    def __init__(self, chat_id: str, history: list[str], last_user_message: str):
        self.chat_id = chat_id
        self.history = history
        self.last_user_message = last_user_message
