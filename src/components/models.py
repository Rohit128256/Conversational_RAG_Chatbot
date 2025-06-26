import os
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama, OllamaEmbeddings
from dotenv import load_dotenv
load_dotenv()

# Groq inference API key
groq_api_key = os.getenv("GROQ_API_KEY")

# Different Models
ollama_model = ChatOllama(model="llama3.1:8b")
groq_model = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct",groq_api_key=groq_api_key)

# Embedding Models
ollama_embedding = OllamaEmbeddings(model="nomic-embed-text:v1.5")
