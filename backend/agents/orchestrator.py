"""Orchestrator Agent - Routes and coordinates the RAG pipeline."""

from typing import Any, Dict

from .state import RAGState, rag_state_to_dict


def orchestrator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestrator Agent: Receives query, validates, and determines routing.
    Detects if query needs web search based on time-sensitive keywords.
    """
    query = state.get("query", "").strip()
    if not query:
        return {
            **state,
            "error": "Empty query",
            "final_response": "Please provide a non-empty question.",
        }

    # Detect if web search is needed
    web_keywords = [
        "today", "latest", "current", "news", "recent", "now", 
        "2024", "2025", "2026", "this week", "this month", "this year",
        "trending", "breaking", "update", "new"
    ]
    query_lower = query.lower()
    needs_web_search = any(keyword in query_lower for keyword in web_keywords)

    return {
        **state,
        "query": query,
        "needs_web_search": needs_web_search,
        "error": None,
    }

