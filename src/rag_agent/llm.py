"""LLM factory utilities."""
from __future__ import annotations

from langchain_groq import ChatGroq

from .config import settings


def get_llm():
    """Return a chat model instance based on configured provider."""
    provider = settings.chat_provider
    if provider == "groq":
        # Verify Groq API key is set
        import os
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "gsk-your-groq-key":
            raise ValueError(
                "Groq API key not configured. Please set GROQ_API_KEY in your .env file "
                "or environment variables."
            )
        # Configure Groq with parameters matching the example implementation
        # Note: top_p must be passed via model_kwargs in langchain-groq
        model_kwargs = {
            "top_p": settings.groq_top_p,
        }
        
        
        kwargs = {
            "model": settings.chat_model,
            "temperature": settings.groq_temperature,
            "max_tokens": settings.groq_max_tokens,
            "model_kwargs": model_kwargs,
        }
        
        # Add reasoning_effort via kwargs (for models that support it like gpt-oss-20b)
        if settings.groq_reasoning_effort:
            kwargs["reasoning_effort"] = settings.groq_reasoning_effort
        
        # Support custom base URL for OpenAI-compatible endpoints
        if settings.groq_base_url:
            kwargs["base_url"] = settings.groq_base_url
            
        return ChatGroq(**kwargs)
    raise ValueError(
        "Unsupported chat provider. Use 'groq'. "
        "Override via RAG_CHAT_PROVIDER env var."
    )


__all__ = ["get_llm"]

