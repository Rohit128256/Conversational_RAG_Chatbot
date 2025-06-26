import os
from pathlib import Path

from src.components.vector_store import vector_db
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFium2Loader, TextLoader, UnstructuredFileLoader


def add_info_from_file(file_path: str) -> None:
    """
    Load a document from a file, split it into chunks, and add to the Chroma vector database.

    Args:
        file_path (str): Path to the document file (e.g., .pdf, .txt, or other supported formats).
    """
    # Resolve absolute path
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # Choose an appropriate loader based on file extension
    ext = path.suffix.lower()
    if ext == ".pdf":
        loader = PyPDFium2Loader(str(path))
    elif ext in {".txt", ".md", ".csv"}:
        loader = TextLoader(str(path))
    else:
        # Fallback for other file types (e.g., .docx, .html)
        loader = UnstructuredFileLoader(str(path))

    # Load raw documents
    raw_docs = loader.load()
    if not raw_docs:
        raise ValueError(f"No documents loaded from {path}")

    # Initialize the text splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=300
    )

    # Split documents into smaller chunks
    chunked_docs = splitter.split_documents(raw_docs)

    # Adding metadata in order to shrink the search space for future use 
    for doc in chunked_docs:
        doc.metadata["type"] = "external_docs"

    # Add documents to the vector store
    vector_db.add_documents(chunked_docs)
