"""Project wide configuration helpers."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(slots=True)
class Settings:
    """Runtime configuration for the RAG agent."""

    data_dir: Path = Path(os.getenv("RAG_DATA_DIR", "data/docs"))
    vector_dir: Path = Path(os.getenv("RAG_VECTOR_DIR", "artifacts/vectorstore"))
    embedding_provider: str = os.getenv("RAG_EMBEDDING_PROVIDER", "huggingface").lower()
    embedding_model: str = os.getenv("RAG_EMBEDDING_MODEL", "text-embedding-3-small")
    hf_embedding_model: str = os.getenv(
        "RAG_HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    chat_provider: str = os.getenv("RAG_CHAT_PROVIDER", "groq").lower()
    chat_model: str = os.getenv("RAG_CHAT_MODEL", "openai/gpt-oss-20b")
    groq_base_url: str = os.getenv("GROQ_BASE_URL", "")
    groq_temperature: float = float(os.getenv("GROQ_TEMPERATURE", "0.7"))
    groq_max_tokens: int = int(os.getenv("GROQ_MAX_TOKENS", "8192"))
    groq_top_p: float = float(os.getenv("GROQ_TOP_P", "1.0"))
    groq_reasoning_effort: str = os.getenv("GROQ_REASONING_EFFORT", "medium")
    chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "800"))
    chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "120"))

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vector_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
