from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

session_hist = {}

def get_session_history(session_id : str) -> BaseChatMessageHistory:
    if session_id not in session_hist:
        session_hist[session_id] = ChatMessageHistory()
    return session_hist[session_id]