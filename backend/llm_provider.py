"""Centralized LLM provider with automatic Gemini -> Ollama fallback."""

import os
from typing import Optional, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable, RunnableLambda

# Try importing both providers
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("[LLM] Warning: langchain-google-genai not installed")

try:
    from langchain_ollama import ChatOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("[LLM] Warning: langchain-ollama not installed")


def create_fallback_wrapper(gemini_llm, ollama_llm):
    """Create a Runnable that wraps Gemini with Ollama fallback."""
    
    def invoke_with_fallback(input_data, **kwargs):
        """Try Gemini first, fall back to Ollama on any error."""
        # Try Gemini first
        if gemini_llm:
            try:
                return gemini_llm.invoke(input_data, **kwargs)
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check if it's a rate limit error
                if "429" in str(e) or "resource_exhausted" in error_msg or "quota" in error_msg:
                    print(f"[LLM] Gemini rate limit hit, falling back to Ollama...")
                else:
                    print(f"[LLM] Gemini error ({e}), falling back to Ollama...")
                
                # Fall through to Ollama
                if ollama_llm:
                    print("[LLM] Using Ollama fallback")
                    return ollama_llm.invoke(input_data, **kwargs)
                else:
                    raise e
        
        # If no Gemini or Gemini failed and we have Ollama
        if ollama_llm:
            return ollama_llm.invoke(input_data, **kwargs)
        
        raise RuntimeError("No LLM available")
    
    return RunnableLambda(invoke_with_fallback)


def get_llm(temperature: float = 0.4, max_tokens: int = 2048) -> Runnable:
    """
    Get an LLM Runnable with automatic fallback: Gemini -> Ollama.
    Uses standard LangChain .with_fallbacks() mechanism.
    """
    primary_llm = None
    fallback_llm = None
    
    # Initialize primary (Gemini)
    if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY", "").strip():
        try:
            model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
            primary_llm = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=os.getenv("GEMINI_API_KEY"),
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            print(f"[LLM] Primary: Google Gemini ({model})")
        except Exception as e:
            print(f"[LLM] Gemini init failed: {e}")
            
    # Initialize fallback (Ollama)
    if OLLAMA_AVAILABLE:
        try:
            model = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            fallback_llm = ChatOllama(
                model=model,
                base_url=base_url,
                temperature=temperature,
                num_predict=max_tokens,
            )
            print(f"[LLM] Fallback: Ollama ({model})")
        except Exception as e:
            print(f"[LLM] Ollama init failed: {e}")

    # Return appropriate LLM configuration
    if primary_llm and fallback_llm:
        # Use RunnableLambda wrapper for better fallback handling
        return create_fallback_wrapper(primary_llm, fallback_llm)
    elif primary_llm:
        return primary_llm
    elif fallback_llm:
        print("[LLM] Using Ollama only (Gemini not available)")
        return fallback_llm
    else:
        raise RuntimeError("No LLM provider available! Please check .env configuration.")


