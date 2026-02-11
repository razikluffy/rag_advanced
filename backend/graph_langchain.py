"""LangGraph RAG pipeline with proper LangChain/LangGraph patterns.

This module builds the RAG workflow graph using:
- StateGraph for workflow orchestration
- Proper TypedDict state schema
- LangChain Runnables as nodes
- Conditional edges for routing
"""

from typing import Any, Dict, Literal, TypedDict, Annotated, Optional, List
from operator import add

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from agents.state import RAGState
from agents.orchestrator import OrchestratorAgent
from agents.query_analysis import QueryAnalysisAgent
from agents.retrieval_langchain import RetrievalAgent
from agents.reranking import ReRankingAgent
from agents.relevance_checker import RelevanceCheckerAgent
from agents.generation import GenerationAgent
from agents.citation import CitationAgent
from agents.chains import (
    create_query_analysis_node,
    create_relevance_check_node,
    create_generation_node
)


# ============================================================================
# State Schema (TypedDict for LangGraph)
# ============================================================================

class RAGGraphState(TypedDict):
    """State schema for LangGraph RAG pipeline.
    
    Using TypedDict instead of Pydantic for LangGraph compatibility.
    """
    # Input
    query: str
    session_id: Optional[str]
    conversation_history: List[Dict[str, Any]]
    
    # Orchestrator output
    needs_web_search: bool
    error: Optional[str]
    
    # Query Analysis output
    query_intent: Optional[str]
    query_entities: List[str]
    query_type: Optional[str]
    
    # Retrieval output
    retrieved_chunks: List[Any]
    
    # Re-ranking output
    reranked_chunks: List[Any]
    
    # Relevance output
    relevance_score: int
    relevance_reasoning: str
    
    # Generation output
    generated_answer: str
    
    # Citation output
    citations: List[Dict[str, Any]]
    final_response: str


# ============================================================================
# Helper Functions
# ============================================================================

def convert_to_graph_state(rag_state: RAGState) -> RAGGraphState:
    """Convert Pydantic RAGState to TypedDict RAGGraphState."""
    return {
        "query": rag_state.query,
        "session_id": rag_state.session_id,
        "conversation_history": rag_state.conversation_history,
        "needs_web_search": False,
        "error": rag_state.error,
        "query_intent": rag_state.query_intent,
        "query_entities": rag_state.query_entities,
        "query_type": rag_state.query_type,
        "retrieved_chunks": rag_state.retrieved_chunks,
        "reranked_chunks": rag_state.reranked_chunks,
        "relevance_score": 0,
        "relevance_reasoning": "",
        "generated_answer": rag_state.generated_answer,
        "citations": rag_state.citations,
        "final_response": rag_state.final_response,
    }


def convert_from_graph_state(state: RAGGraphState) -> RAGState:
    """Convert TypedDict back to Pydantic RAGState."""
    return RAGState(
        query=state.get("query", ""),
        session_id=state.get("session_id"),
        conversation_history=state.get("conversation_history", []),
        query_intent=state.get("query_intent"),
        query_entities=state.get("query_entities", []),
        query_type=state.get("query_type"),
        retrieved_chunks=state.get("retrieved_chunks", []),
        reranked_chunks=state.get("reranked_chunks", []),
        generated_answer=state.get("generated_answer", ""),
        citations=state.get("citations", []),
        final_response=state.get("final_response", ""),
        error=state.get("error"),
    )


# ============================================================================
# Graph Builder
# ============================================================================

def build_rag_graph(
    vector_db_mcp, 
    web_search_mcp=None,
    checkpointer=None,
    debug: bool = False
):
    """Build the LangGraph RAG pipeline.
    
    Args:
        vector_db_mcp: VectorDB MCP server instance
        web_search_mcp: Optional WebSearch MCP server
        checkpointer: Optional checkpoint saver (e.g., MemorySaver)
        debug: Enable debug logging
        
    Returns:
        Compiled LangGraph workflow
    """
    
    # Initialize Agents
    orchestrator = OrchestratorAgent()
    query_analysis = QueryAnalysisAgent()
    retrieval = RetrievalAgent(
        vector_db_mcp=vector_db_mcp,
        web_search_mcp=web_search_mcp,
        retriever_type="hybrid",
        top_k=15,
        use_web_fallback=False  # We'll handle web search separately
    )
    reranking = ReRankingAgent()
    relevance_checker = RelevanceCheckerAgent()
    generation = GenerationAgent()
    citation = CitationAgent()
    
    # Alternative: Use LangChain Runnable nodes
    # query_analysis_node = create_query_analysis_node()
    # relevance_check_node = create_relevance_check_node()
    # generation_node = create_generation_node()
    
    # Create Graph
    workflow = StateGraph(RAGGraphState)
    
    # Add Nodes (using class-based agents)
    workflow.add_node("orchestrator", lambda state: orchestrator.invoke(dict(state)))
    workflow.add_node("query_analysis", lambda state: query_analysis.invoke(dict(state)))
    workflow.add_node("retrieval", lambda state: retrieval.invoke(dict(state)))
    workflow.add_node("reranking", lambda state: reranking.invoke(dict(state)))
    workflow.add_node("relevance_checker", lambda state: relevance_checker.invoke(dict(state)))
    workflow.add_node("generation", lambda state: generation.invoke(dict(state)))
    workflow.add_node("citation", lambda state: citation.invoke(dict(state)))
    
    # Optional: Web search node for explicit web search path
    def web_search_node(state: RAGGraphState) -> RAGGraphState:
        """Explicit web search node."""
        if web_search_mcp:
            query = state.get("query", "")
            resp = web_search_mcp.call("search", query=query, top_k=5)
            
            if resp.success and resp.result:
                results = resp.result.get("results", [])
                from langchain_core.documents import Document
                web_docs = []
                for result in results:
                    web_docs.append(Document(
                        page_content=f"{result.get('title', '')}\n\n{result.get('snippet', '')}",
                        metadata={
                            "source": result.get("url", "web"),
                            "type": "web_search",
                            "page": "web",
                            "title": result.get("title", "Web Result")
                        }
                    ))
                
                print(f"[Web Search Node] Retrieved {len(web_docs)} web results")
                
                # Merge with any existing retrieved chunks
                existing = state.get("retrieved_chunks", [])
                return {**state, "retrieved_chunks": web_docs + existing, "needs_web_search": True}
        
        return state
    
    workflow.add_node("web_search", web_search_node)
    
    # Define Entry Point
    workflow.set_entry_point("orchestrator")
    
    # Define Standard Edges
    workflow.add_edge("orchestrator", "query_analysis")
    workflow.add_edge("query_analysis", "retrieval")
    workflow.add_edge("retrieval", "reranking")
    workflow.add_edge("reranking", "relevance_checker")
    
    # Conditional Routing from Relevance Checker
    def route_after_relevance(state: RAGGraphState) -> Literal["web_search", "generation"]:
        """Route to web search if relevance is low, otherwise to generation."""
        score = state.get("relevance_score", 0)
        needs_web = state.get("needs_web_search", False)
        already_tried_web = any(
            doc.metadata.get("type") == "web_search" 
            for doc in state.get("retrieved_chunks", [])
            if hasattr(doc, "metadata")
        )
        
        # Route to web search if:
        # 1. Relevance score is low (< 5)
        # 2. Web search is needed (time-sensitive query)
        # 3. Haven't already tried web search
        if (score < 5 or needs_web) and not already_tried_web and web_search_mcp:
            print(f"[Router] Low relevance ({score}/10) or needs web, routing to web search")
            return "web_search"
        
        print(f"[Router] Sufficient relevance ({score}/10), routing to generation")
        return "generation"
    
    workflow.add_conditional_edges(
        "relevance_checker",
        route_after_relevance,
        {
            "web_search": "web_search",
            "generation": "generation"
        }
    )
    
    # Web search goes directly to generation (skip re-ranking for web results)
    workflow.add_edge("web_search", "generation")
    
    # Generation to Citation to End
    workflow.add_edge("generation", "citation")
    workflow.add_edge("citation", END)
    
    # Compile with optional checkpointing
    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    
    return workflow.compile()


def build_simple_rag_graph(vector_db_mcp, web_search_mcp=None):
    """Build a simplified RAG graph without relevance checking.
    
    This is a faster version that skips the relevance check node.
    """
    
    # Initialize Agents
    orchestrator = OrchestratorAgent()
    query_analysis = QueryAnalysisAgent()
    retrieval = RetrievalAgent(
        vector_db_mcp=vector_db_mcp,
        web_search_mcp=web_search_mcp,
        retriever_type="hybrid"
    )
    reranking = ReRankingAgent()
    generation = GenerationAgent()
    citation = CitationAgent()
    
    # Create Graph
    workflow = StateGraph(RAGGraphState)
    
    # Add Nodes
    workflow.add_node("orchestrator", lambda state: orchestrator.invoke(dict(state)))
    workflow.add_node("query_analysis", lambda state: query_analysis.invoke(dict(state)))
    workflow.add_node("retrieval", lambda state: retrieval.invoke(dict(state)))
    workflow.add_node("reranking", lambda state: reranking.invoke(dict(state)))
    workflow.add_node("generation", lambda state: generation.invoke(dict(state)))
    workflow.add_node("citation", lambda state: citation.invoke(dict(state)))
    
    # Simple linear flow
    workflow.set_entry_point("orchestrator")
    workflow.add_edge("orchestrator", "query_analysis")
    workflow.add_edge("query_analysis", "retrieval")
    workflow.add_edge("retrieval", "reranking")
    workflow.add_edge("reranking", "generation")
    workflow.add_edge("generation", "citation")
    workflow.add_edge("citation", END)
    
    return workflow.compile()


def build_agentic_rag_graph(vector_db_mcp, web_search_mcp=None):
    """Build an agentic RAG graph with tool use.
    
    This version uses LangChain tools for a more flexible agent-based approach.
    """
    from langchain.agents import create_react_agent, AgentExecutor
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    from agents.tools import create_tools
    from llm_provider import get_llm
    
    # Create tools
    tools = create_tools(vector_db_mcp, web_search_mcp, None)
    
    # Create agent prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", 
         "You are a helpful RAG assistant. Use the available tools to retrieve information\n"
         "and answer the user's question accurately.\n\n"
         "Available tools:\n"
         "- vector_db_search: Search uploaded documents\n"
         "- web_search: Search the web for current information\n\n"
         "Always cite your sources."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create ReAct agent
    llm = get_llm(temperature=0.4)
    agent = create_react_agent(llm, tools, prompt)
    
    # Wrap in executor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    return agent_executor
