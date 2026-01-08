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
        
        
        # Define Model Hierarchy for Resilience
        
        # 0. Base Configuration
        base_kwargs = {
            "temperature": settings.groq_temperature,
            "max_tokens": settings.groq_max_tokens,
            "model_kwargs": {"top_p": settings.groq_top_p},
            "streaming": True,
        }
        
        # 1. Primary Model (Configured in .env or default)
        primary_model = ChatGroq(model=settings.chat_model, **base_kwargs)
        
        # 2. Fallbacks (Hardcoded High-Performance Alternatives)
        fallbacks = [
            ChatGroq(model="mixtral-8x7b-32768", **base_kwargs), # Excellent alternative
            ChatGroq(model="llama3-70b-8192", **base_kwargs),    # Strong redundant
            ChatGroq(model="llama3-8b-8192", **base_kwargs),     # Fast backup
            ChatGroq(model="gemma2-9b-it", **base_kwargs),       # Emergency backup
        ]
        
        # 3. Create Fallback Chain
        # This will automatically catch 429/5xx errors and try the next model
        llm_with_fallbacks = primary_model.with_fallbacks(
            fallbacks,
            exceptions_to_handle=(ValueError, Exception) # Catch-all for API errors
        )
        
        return llm_with_fallbacks
    if provider == "google":
        import os
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
             # Try to find it in GROQ_API_KEY if the user just pasted it there
             possible_key = os.getenv("GROQ_API_KEY", "")
             if possible_key.startswith("AIza"):
                 api_key = possible_key
                 
        if not api_key:
            raise ValueError("Google API Key not found. Set GOOGLE_API_KEY.")
            
        # 1. Primary Model (Use stable 001/002 versions or 'gemini-pro')
        # Trying 'gemini-1.5-flash-latest' which translates to the latest valid endpoint
        primary_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest", 
            google_api_key=api_key,
            temperature=settings.groq_temperature,
            convert_system_message_to_human=True
        )
        
        # 2. Fallbacks (Safe bets)
        fallbacks = [
            ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key),
            ChatGoogleGenerativeAI(model="gemini-1.0-pro", google_api_key=api_key),
        ]
        
        return primary_model.with_fallbacks(fallbacks)

    if provider == "openai":
        import os
        from langchain_openai import ChatOpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
             # Try to find it in GROQ_API_KEY or GOOGLE_API_KEY if the user just pasted it there
             possible_key = os.getenv("GROQ_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
             if "sk-" in possible_key:
                 api_key = possible_key

        if not api_key:
            raise ValueError("OpenAI API Key not found. Set OPENAI_API_KEY.")

        # 1. Primary Model (GPT-4o is the current standard)
        primary_model = ChatOpenAI(
            model="gpt-4o",
            openai_api_key=api_key,
            temperature=settings.groq_temperature,
            streaming=True
        )
        
        # 2. Fallbacks
        fallbacks = [
            ChatOpenAI(model="gpt-4-turbo", openai_api_key=api_key),
            ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=api_key),
        ]
        
        return primary_model.with_fallbacks(fallbacks)

    raise ValueError(
        f"Unsupported chat provider '{provider}'. Use 'groq', 'google', or 'openai'."
    )


__all__ = ["get_llm"]

