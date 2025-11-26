"""Embedding factory utilities."""
from __future__ import annotations

import os
import warnings

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings 

from .config import settings

# Fix for PyTorch meta tensor issue
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")
# Disable accelerate meta device to avoid meta tensor errors
os.environ.setdefault("ACCELERATE_USE_CPU", "1")

# Suppress PyTorch internal warnings
warnings.filterwarnings("ignore", message=".*torch.classes.*")
warnings.filterwarnings("ignore", category=UserWarning, module="torch")


def get_embeddings():
    """Return an embeddings instance based on configured provider."""
    provider = settings.embedding_provider
    if provider == "openai":
        return OpenAIEmbeddings(model=settings.embedding_model)
    if provider == "huggingface":
        # Configure to use CPU and avoid meta tensor issues
        return HuggingFaceEmbeddings(
            model_name=settings.hf_embedding_model,
            model_kwargs={
                "device": "cpu",
                "trust_remote_code": True,
            },
            encode_kwargs={
                "normalize_embeddings": False,
            },
        )
    raise ValueError(
        "Unsupported embedding provider. Use 'openai' or 'huggingface'. "
        "Override via RAG_EMBEDDING_PROVIDER env var."
    )


__all__ = ["get_embeddings"]
