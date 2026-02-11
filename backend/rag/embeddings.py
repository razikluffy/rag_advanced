"""Embeddings via Google Gemini (gemini-embedding-001) for fast, high-quality embeddings."""

from typing import List
import os

# Primary: Google Gemini Embeddings (fast, cloud-based)
try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Fallback: Ollama embeddings
try:
    from langchain_community.embeddings import OllamaEmbeddings
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


def get_embedder(model: str = "models/gemini-embedding-001"):
    """
    Return an embedder compatible with LangChain.
    
    Priority:
    1. Google Gemini gemini-embedding-001 (supported in Gemini API v1beta)
    2. Ollama nomic-embed-text (fallback, local)
    3. Fake embeddings (last resort)
    
    Args:
        model: Embedding model name
            - "models/gemini-embedding-001" (Gemini, recommended)
            - "nomic-embed-text" (Ollama fallback)
    """
    # Try Gemini first (fastest option)
    if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"):
        try:
            print(f"[Embeddings] Using Google Gemini: {model}")
            return GoogleGenerativeAIEmbeddings(
                model=model,
                task_type="retrieval_document"
            )
        except Exception as e:
            print(f"[Embeddings] Gemini init failed: {e}, falling back to Ollama")
    
    # Fallback to Ollama
    if OLLAMA_AVAILABLE:
        print("[Embeddings] Using Ollama: nomic-embed-text")
        return OllamaEmbeddings(model="nomic-embed-text")
    
    # Last resort: Fake embeddings
    print("[Embeddings] WARNING: Using fake embeddings (no Gemini or Ollama available)")
    return _FakeEmbeddings()


class _FakeEmbeddings:
    """Fallback when neither Gemini nor Ollama is available - returns deterministic vectors."""

    def __init__(self, dim: int = 768):
        self.dim = dim

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        import hashlib
        import struct
        out = []
        for t in texts:
            h = hashlib.sha256(t.encode()).digest()
            vec = [struct.unpack("f", h[i:i+4])[0] % 0.1 for i in range(0, min(len(h), self.dim * 4), 4)]
            while len(vec) < self.dim:
                vec.append(0.0)
            out.append(vec[:self.dim])
        return out

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]
