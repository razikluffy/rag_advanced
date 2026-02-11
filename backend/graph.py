"""LangGraph RAG pipeline: Orchestrator -> QueryAnalysis -> Retrieval -> ReRanking -> RelevanceCheck -> Generation -> Citation."""

from typing import Any, Dict, Literal, TypedDict

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from agents import (
    orchestrator_node,
    retrieval_node,
    reranking_node,
    generation_node,
    citation_node,
)
from agents.agent_wrapper import (
    query_analysis_node as langchain_query_analysis_node,
    relevance_check_node as langchain_relevance_check_node,
)


# State schema for LangGraph (mutable dict)
class RAGGraphState(TypedDict, total=False):
    query: str
    session_id: str
    conversation_history: list
    query_intent: str
    query_entities: list
    query_type: str
    needs_web_search: bool
    relevance_score: int
    relevance_reasoning: str
    retrieved_chunks: list
    reranked_chunks: list
    generated_answer: str
    citations: list
    final_response: str
    error: str


def build_rag_graph(vector_db_mcp, web_search_mcp=None):
    """Build the LangGraph pipeline with MCP injection and relevance checking."""

    def retrieval_with_mcp(state: Dict[str, Any]) -> Dict[str, Any]:
        return retrieval_node(state, vector_db_mcp, web_search_mcp)

    def should_use_web_search(state: Dict[str, Any]) -> Literal["web_search", "generation"]:
        """Conditional routing: use web search if documents are irrelevant or time-sensitive."""
        # Check if web search is needed (either time-sensitive or low relevance)
        if state.get("needs_web_search", False):
            print("[Routing] → Using web search (flagged as needed)")
            return "web_search"
        print("[Routing] → Using knowledge base documents")
        return "generation"

    graph = StateGraph(RAGGraphState)

    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("query_analysis", langchain_query_analysis_node)
    graph.add_node("retrieval", retrieval_with_mcp)
    graph.add_node("reranking", reranking_node)
    graph.add_node("relevance_check", langchain_relevance_check_node)
    graph.add_node("generation", generation_node)
    graph.add_node("citation", citation_node)
    
    # Add web_search node that re-runs retrieval with web search flag
    def web_search_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """Re-run retrieval with web search enabled."""
        print("[Web Search] Retrieving from web...")
        state_with_web = {**state, "needs_web_search": True}
        return retrieval_node(state_with_web, vector_db_mcp, web_search_mcp)
    
    graph.add_node("web_search", web_search_node)

    graph.set_entry_point("orchestrator")
    graph.add_edge("orchestrator", "query_analysis")
    graph.add_edge("query_analysis", "retrieval")
    graph.add_edge("retrieval", "reranking")
    graph.add_edge("reranking", "relevance_check")
    
    # Conditional routing after relevance check
    graph.add_conditional_edges(
        "relevance_check",
        should_use_web_search,
        {
            "web_search": "web_search",
            "generation": "generation"
        }
    )
    
    graph.add_edge("web_search", "generation")
    graph.add_edge("generation", "citation")
    graph.add_edge("citation", END)

    return graph.compile()

