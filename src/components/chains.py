from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.output_parsers import StrOutputParser
from src.components.prompts import search_query_prompt, qa_prompt
from src.components.models import ollama_model, groq_model

#  making the rephrase or search query generator chain using LLM chain 
search_query_chain = search_query_prompt | groq_model | StrOutputParser()
search_query_chain2 = search_query_prompt | ollama_model | StrOutputParser()

# Creating a stuff_doc documents chain
qa_stuff_chain = create_stuff_documents_chain(
    llm=groq_model,
    prompt=qa_prompt,
    document_variable_name="context"
)

qa_stuff_chain2 = create_stuff_documents_chain(
    llm=ollama_model,
    prompt=qa_prompt,
    document_variable_name="context"
)

