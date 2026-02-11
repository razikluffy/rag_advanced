"""Shared state for LangGraph RAG pipeline."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RAGState(BaseModel):
    """State passed between LangGraph nodes."""

    query: str = ""
    session_id: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Query Analysis output
    query_intent: Optional[str] = None
    query_entities: List[str] = Field(default_factory=list)
    query_type: Optional[str] = None

    # Retrieval output
    retrieved_chunks: List[Dict[str, Any]] = Field(default_factory=list)

    # Re-ranking output
    reranked_chunks: List[Dict[str, Any]] = Field(default_factory=list)

    # Generation output
    generated_answer: str = ""

    # Citation output
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    final_response: str = ""

    # Controls
    error: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"


def rag_state_to_dict(state: RAGState) -> Dict[str, Any]:
    """Convert RAGState to dict for LangGraph."""
    return state.model_dump() if hasattr(state, "model_dump") else state.dict()


def dict_to_rag_state(d: Dict[str, Any]) -> RAGState:
    """Convert dict to RAGState."""
    return RAGState(**{k: v for k, v in d.items() if k in RAGState.model_fields})
