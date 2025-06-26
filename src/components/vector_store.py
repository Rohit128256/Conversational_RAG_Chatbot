import os
from langchain_chroma import Chroma
from src.components.models import ollama_embedding

# current path
current_dir = os.path.dirname(os.path.abspath(__file__))

# Two levels up → project root
main_project_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))

# Chroma persistence folder
persist_dir = os.path.join(main_project_dir, 'vector_db_store')
os.makedirs(persist_dir, exist_ok=True)

vector_db = Chroma(
    collection_name="knowledge_base_and_memory",
    embedding_function=ollama_embedding,
    persist_directory=persist_dir
)