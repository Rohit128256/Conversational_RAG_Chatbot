from langchain_core.documents import Document
from src.session import get_session_history
from src.components.retrievers import get_message_retriever, content_retriever
from src.components.chains import search_query_chain, qa_stuff_chain
from src.components.vector_store import vector_db
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnableWithMessageHistory, ConfigurableFieldSpec



def hybrid_runnable_fn(inputs: dict, config: RunnableConfig | None = None) -> dict:
    # Get session_id from config instead of inputs
    if config is None or "configurable" not in config or "session_id" not in config["configurable"]:
        raise ValueError("Session ID not found in config")
    user_id = config["configurable"]["session_id"]
    
    user_question = inputs["input"]
    full_history = inputs.get("chat_history", [])

    # Pull just the last N messages from full_history for recency -
    N = 15
    last_N = full_history[-N:] if len(full_history) >= N else full_history
    recency_text = "\n\n".join(
        f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
        for m in last_N
    )

    # Semantic retrieve older memory from Chroma (filtered by user_id) -
    memory_retriever = get_message_retriever(user_id)
    memory_docs = memory_retriever.invoke(user_question)
    older_context = "\n\n".join(doc.page_content for doc in memory_docs)


    # Rephrase + retrieve from external KB - (to make the search query)
    rephrased_query = search_query_chain.invoke({
        "old_related_memory": older_context,
        "recent_memory" : recency_text,
        "input": user_question
    }).strip()
    kb_docs = content_retriever.invoke(rephrased_query)
    # kb_context = "\n\n".join(doc.page_content for doc in kb_docs)

    # Stuff into final prompt -
    answer_text = qa_stuff_chain.invoke({
        "context": kb_docs,
        "old_memory_context": older_context,
        "recent_memory_context" : recency_text,
        "input": user_question
    })

    # Persist this turn as a new chat_memory doc in Chroma ─────────────
    new_chat_doc = Document(
        page_content=f"User: {user_question}\nAssistant: {answer_text}",
        metadata={"type": "chat_memory", "user_id": user_id}
    )
    vector_db.add_documents([new_chat_doc])

    # Build updated history for RunnableWithMessageHistory ──────────────
    updated_history = full_history + [
        HumanMessage(content=user_question),
        AIMessage(content=answer_text)
    ]

    return {
        "answer": answer_text,
        "chat_history": updated_history
    }


hybrid_runnable = RunnableLambda(func=hybrid_runnable_fn)

runnable_with_history = RunnableWithMessageHistory(
    hybrid_runnable,
    get_session_history,
    input_messages_key="input",        # takes {"input": ...}
    history_messages_key="chat_history",  # separate key for full history
    output_messages_key="answer",         # what key your inner fn returns
    history_factory_config=[
        ConfigurableFieldSpec(
            id="session_id",
            annotation=str,
            name="Session ID",
            description="Unique identifier for this session.",
            default="",
            is_shared=True
        )
    ]
)