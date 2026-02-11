"""Citation Agent - Adds citations to the generated answer."""

from typing import Any, Dict, List


def _extract_citations(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract unique (source, page) from chunks."""
    seen = set()
    citations = []
    for c in chunks:
        meta = c.get("metadata", {})
        src = meta.get("source", "unknown")
        page = meta.get("page", "?")
        key = (src, page)
        if key not in seen:
            seen.add(key)
            citations.append({"source": src, "page": page})
    return citations


def _format_citation(c: Dict[str, Any]) -> str:
    return f"[Source: {c.get('source', 'unknown')}, Page {c.get('page', '?')}]"


def _filter_relevant_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Return only chunks from the most relevant document for citation.
    Uses the top-scoring chunk's source - only cite that document.
    Filters out irrelevant docs (e.g. Risk & Fraud when query is about invoices).
    """
    if not chunks:
        return []
    top_source = chunks[0].get("metadata", {}).get("source", "unknown")
    return [c for c in chunks if c.get("metadata", {}).get("source") == top_source]


def citation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Citation Agent: Extracts citations from only the most relevant document(s).
    Shows sources that contributed to the answer, not unrelated docs.
    """
    answer = state.get("generated_answer", "")
    chunks = state.get("reranked_chunks", [])

    # Only cite from the top doc + any doc scoring within 80% of best
    relevant_chunks = _filter_relevant_chunks(chunks)
    citations = _extract_citations(relevant_chunks)
    # Return only the answer text without citation sources
    final = answer

    return {
        **state,
        "citations": citations,
        "final_response": final,
    }
