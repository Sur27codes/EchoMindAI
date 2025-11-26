"""Document ingestion and vector-store persistence."""
from __future__ import annotations

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS

from .config import settings
from .embeddings import get_embeddings


def load_documents() -> list:
    """Load documents from the configured data directory based on file extension."""
    settings.ensure_dirs()
    documents = []
    
    # Define supported extensions and their loaders
    # Note: We import loaders inside the function to avoid top-level dependency issues
    # if dependencies are missing during initial setup/healthcheck
    from langchain_community.document_loaders import (
        PyPDFLoader, 
        UnstructuredImageLoader, 
        TextLoader
    )

    for file_path in settings.data_dir.rglob("*"):
        if file_path.is_file():
            try:
                if file_path.suffix.lower() == ".pdf":
                    loader = PyPDFLoader(str(file_path))
                    documents.extend(loader.load())
                elif file_path.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                    loader = UnstructuredImageLoader(str(file_path))
                    documents.extend(loader.load())
                elif file_path.suffix.lower() in [".txt", ".md"]:
                    loader = TextLoader(str(file_path), encoding="utf-8")
                    documents.extend(loader.load())
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                
    if not documents:
        raise FileNotFoundError(
            f"No supported documents found in {settings.data_dir}. "
            "Add .txt, .md, .pdf, .png, .jpg, or .jpeg files."
        )
    return documents


def split_documents(documents: list) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    return splitter.split_documents(documents)


def build_vector_store(chunks: list) -> FAISS:
    embeddings = get_embeddings()
    return FAISS.from_documents(chunks, embeddings)


def ingest_documents() -> str:
    """Run the end-to-end ingestion pipeline and persist FAISS index."""
    documents = load_documents()
    chunks = split_documents(documents)
    vector_store = build_vector_store(chunks)
    vector_store.save_local(str(settings.vector_dir), index_name="projectx")
    return str(settings.vector_dir)


__all__ = [
    "ingest_documents",
]
