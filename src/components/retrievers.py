from src.components.vector_store import vector_db

# Making two different retrievers to fetch context and previous messages seperately
content_retriever = vector_db.as_retriever(search_kwargs={"k": 5, "filter":
        {"type": "external_docs"}
            })

def get_message_retriever(session_id : str):
    return vector_db.as_retriever(search_kwargs={"k": 8, "filter":{
        "$and" : [
            {"type" : "chat_memory"},
            {"user_id" : session_id}
        ]
            }})