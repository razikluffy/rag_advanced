"""
LangChain Integration Examples for RAG System
==============================================

This file demonstrates how to use all the new LangChain components
in your RAG system.

Environment Variables:
- USE_LANGCHAIN=true              # Enable LangChain components
- USE_LANGCHAIN_MEMORY=true       # Use LangChain memory
- USE_LANGCHAIN_RETRIEVER=true    # Use LangChain retrievers
- USE_LANGCHAIN_GRAPH=true        # Use LangGraph-based graph

Quick Start:
    # Run the backend with all LangChain features enabled
    USE_LANGCHAIN=true python -m backend.main
"""

import os
from pathlib import Path

# Ensure .env is loaded
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


# ============================================================================
# Example 1: Using LangChain Tools
# ============================================================================

def example_tools():
    """Demonstrate using LangChain Tools for MCP operations."""
    
    from mcp_servers import VectorDBMCPServer, WebSearchMCPServer, DocumentProcessingMCPServer
    from agents.tools import create_tools, VectorDBSearchTool, WebSearchTool
    
    # Initialize MCP servers (normally done in main.py)
    from rag import create_vector_store, create_bm25_index, get_embedder
    
    vector_store = create_vector_store()
    bm25_index = create_bm25_index()
    embedder = get_embedder()
    
    vector_db_mcp = VectorDBMCPServer(vector_store, bm25_index, embedder)
    web_search_mcp = WebSearchMCPServer()
    
    # Create LangChain tools
    tools = create_tools(vector_db_mcp, web_search_mcp, None)
    
    print("=== LangChain Tools Example ===")
    print(f"Created {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description[:80]}...")
    
    # Use a tool directly
    vector_tool = next(t for t in tools if t.name == "vector_db_search")
    results = vector_tool.invoke({"query": "What is machine learning?", "top_k": 3})
    
    print(f"\nVector search returned {len(results)} documents")
    for i, doc in enumerate(results[:2]):
        print(f"  {i+1}. {doc.page_content[:100]}...")


# ============================================================================
# Example 2: Using LangChain Retrievers
# ============================================================================

def example_retrievers():
    """Demonstrate using LangChain Retriever interface."""
    
    from mcp_servers import VectorDBMCPServer, WebSearchMCPServer
    from agents import create_retriever, HybridRetriever, VectorRetriever, KeywordRetriever
    from rag import create_vector_store, create_bm25_index, get_embedder
    
    # Initialize
    vector_store = create_vector_store()
    bm25_index = create_bm25_index()
    embedder = get_embedder()
    
    vector_db_mcp = VectorDBMCPServer(vector_store, bm25_index, embedder)
    web_search_mcp = WebSearchMCPServer()
    
    print("\n=== LangChain Retrievers Example ===")
    
    # Create hybrid retriever (vector + keyword + web fallback)
    retriever = create_retriever(
        vector_db_mcp=vector_db_mcp,
        web_search_mcp=web_search_mcp,
        retriever_type="hybrid",
        top_k=10,
        use_web_fallback=True
    )
    
    print(f"Using {type(retriever).__name__}")
    
    # Use retriever.get_relevant_documents()
    query = "What are the latest developments in AI?"
    docs = retriever.get_relevant_documents(query)
    
    print(f"Retrieved {len(docs)} documents for: '{query}'")
    for i, doc in enumerate(docs[:3]):
        source_type = doc.metadata.get("source_type", "unknown")
        print(f"  {i+1}. [{source_type}] {doc.page_content[:80]}...")


# ============================================================================
# Example 3: Using LangChain Memory
# ============================================================================

def example_memory():
    """Demonstrate using LangChain Memory for conversation history."""
    
    from agents.memory_langchain import ConversationBufferMemory, create_memory
    
    print("\n=== LangChain Memory Example ===")
    
    # Create memory
    memory = create_memory(
        memory_key="chat_history",
        return_messages=True,
        k=6,  # Keep last 6 exchanges
        persist_path=None  # Disable persistence for demo
    )
    
    # Simulate conversation
    session_id = "demo_session_123"
    memory.set_session(session_id)
    
    # Add messages
    memory.add_message(session_id, "user", "What is machine learning?")
    memory.add_message(session_id, "assistant", "Machine learning is a subset of AI...")
    memory.add_message(session_id, "user", "How does it differ from deep learning?")
    memory.add_message(session_id, "assistant", "Deep learning is a specific type of ML...")
    
    # Get messages as LangChain format
    messages = memory.get_langchain_messages(session_id)
    print(f"Conversation has {len(messages)} messages")
    for msg in messages:
        print(f"  {msg.type}: {msg.content[:50]}...")
    
    # Load memory variables (for use in chains)
    mem_vars = memory.load_memory_variables({"session_id": session_id})
    chat_history = mem_vars["chat_history"]
    print(f"\nAs LangChain messages: {len(chat_history)} items")


# ============================================================================
# Example 4: Using Individual Chains
# ============================================================================

def example_chains():
    """Demonstrate using individual LCEL chains."""
    
    from agents.chains import (
        create_query_analysis_chain,
        create_relevance_chain,
        create_generation_chain
    )
    
    print("\n=== LangChain LCEL Chains Example ===")
    
    # Query Analysis Chain
    print("\n1. Query Analysis Chain")
    qa_chain = create_query_analysis_chain()
    query = "What are the differences between Python 2 and Python 3?"
    result = qa_chain.invoke({"query": query})
    print(f"  Query: {query}")
    print(f"  Intent: {result.get('query_intent')}")
    print(f"  Type: {result.get('query_type')}")
    print(f"  Entities: {result.get('query_entities', [])}")
    
    # Relevance Chain
    print("\n2. Relevance Chain")
    rel_chain = create_relevance_chain()
    passages = """Passage 1: Python 3 was released in 2008.
Passage 2: Python is a popular programming language."""
    result = rel_chain.invoke({
        "query": "When was Python 3 released?",
        "passages": passages
    })
    print(f"  Relevance Score: {result.get('relevance_score')}/10")
    print(f"  Reasoning: {result.get('reasoning')}")
    
    # Generation Chain
    print("\n3. Generation Chain")
    gen_chain = create_generation_chain()
    from langchain_core.documents import Document
    docs = [
        Document(page_content="Python 3 was released in 2008.", 
                 metadata={"source": "Python Docs", "page": "1"})
    ]
    answer = gen_chain.invoke({
        "query": "When was Python 3 released?",
        "documents": docs,
        "chat_history": []
    })
    print(f"  Generated Answer: {answer[:100]}...")


# ============================================================================
# Example 5: Complete RAG Chain
# ============================================================================

def example_complete_rag_chain():
    """Demonstrate using the complete RAG chain."""
    
    from agents.chains import create_rag_chain
    from agents.memory_langchain import create_memory
    from agents.retriever import HybridRetriever
    from agents.reranking import BAAIReranker
    from mcp_servers import VectorDBMCPServer, WebSearchMCPServer
    from rag import create_vector_store, create_bm25_index, get_embedder
    
    print("\n=== Complete RAG Chain Example ===")
    
    # Initialize components
    vector_store = create_vector_store()
    bm25_index = create_bm25_index()
    embedder = get_embedder()
    
    vector_db_mcp = VectorDBMCPServer(vector_store, bm25_index, embedder)
    web_search_mcp = WebSearchMCPServer()
    
    # Create retriever
    retriever = HybridRetriever(
        vector_db_mcp=vector_db_mcp,
        web_search_mcp=web_search_mcp,
        top_k=10,
        use_web_fallback=True
    )
    
    # Create memory
    memory = create_memory(k=6)
    
    # Create re-ranker
    reranker = BAAIReranker()
    
    # Create complete RAG chain
    rag_chain = create_rag_chain(
        retriever=retriever,
        memory=memory,
        reranker=reranker,
        temperature=0.4,
        max_tokens=2048
    )
    
    # Invoke the chain
    session_id = "rag_demo_session"
    result = rag_chain.invoke({
        "query": "What is the difference between machine learning and AI?",
        "session_id": session_id
    })
    
    print(f"Query: What is the difference between machine learning and AI?")
    print(f"Answer: {result[:150]}...")


# ============================================================================
# Example 6: Using LangGraph
# ============================================================================

def example_langgraph():
    """Demonstrate using the LangGraph-based workflow."""
    
    from graph_langchain import build_rag_graph, build_simple_rag_graph
    from mcp_servers import VectorDBMCPServer, WebSearchMCPServer
    from rag import create_vector_store, create_bm25_index, get_embedder
    
    print("\n=== LangGraph Example ===")
    
    # Initialize
    vector_store = create_vector_store()
    bm25_index = create_bm25_index()
    embedder = get_embedder()
    
    vector_db_mcp = VectorDBMCPServer(vector_store, bm25_index, embedder)
    web_search_mcp = WebSearchMCPServer()
    
    # Build graph
    graph = build_rag_graph(vector_db_mcp, web_search_mcp)
    
    # Create initial state
    state = {
        "query": "What are the latest trends in renewable energy?",
        "session_id": "graph_demo",
        "conversation_history": [],
        "needs_web_search": False,
        "error": None,
        "query_intent": None,
        "query_entities": [],
        "query_type": None,
        "retrieved_chunks": [],
        "reranked_chunks": [],
        "relevance_score": 0,
        "relevance_reasoning": "",
        "generated_answer": "",
        "citations": [],
        "final_response": "",
    }
    
    print(f"Running graph with query: '{state['query']}'")
    result = graph.invoke(state)
    
    print(f"Final Answer: {result.get('final_response', 'No answer')[:150]}...")
    print(f"Citations: {len(result.get('citations', []))} sources")


# ============================================================================
# Example 7: Using as LangChain Agent with Tools
# ============================================================================

def example_agent_with_tools():
    """Demonstrate using the system as a LangChain agent with tools."""
    
    from langchain.agents import create_react_agent, AgentExecutor
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    from agents.tools import create_tools
    from llm_provider import get_llm
    from mcp_servers import VectorDBMCPServer, WebSearchMCPServer
    from rag import create_vector_store, create_bm25_index, get_embedder
    
    print("\n=== Agent with Tools Example ===")
    
    # Initialize
    vector_store = create_vector_store()
    bm25_index = create_bm25_index()
    embedder = get_embedder()
    
    vector_db_mcp = VectorDBMCPServer(vector_store, bm25_index, embedder)
    web_search_mcp = WebSearchMCPServer()
    
    # Create tools
    tools = create_tools(vector_db_mcp, web_search_mcp, None)
    
    # Create agent
    llm = get_llm(temperature=0.4)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", 
         "You are a helpful RAG assistant with access to document search and web search tools.\n"
         "Use the available tools to find information and answer accurately.\n"
         "Available tools:\n"
         "- vector_db_search: Search uploaded documents\n"
         "- web_search: Search the web for current information\n\n"
         "Always cite your sources."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    # Run agent
    result = agent_executor.invoke({
        "input": "What are the key features of Python 3.10?",
        "chat_history": []
    })
    
    print(f"\nAgent Response: {result.get('output', 'No response')[:150]}...")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("LangChain Integration Examples for RAG System")
    print("=" * 60)
    
    # Run examples (comment out ones you don't want to run)
    
    # Example 1: Tools
    try:
        example_tools()
    except Exception as e:
        print(f"Tools example failed: {e}")
    
    # Example 2: Retrievers
    try:
        example_retrievers()
    except Exception as e:
        print(f"Retrievers example failed: {e}")
    
    # Example 3: Memory
    try:
        example_memory()
    except Exception as e:
        print(f"Memory example failed: {e}")
    
    # Example 4: Individual Chains
    try:
        example_chains()
    except Exception as e:
        print(f"Chains example failed: {e}")
    
    # Example 5: Complete RAG Chain
    try:
        example_complete_rag_chain()
    except Exception as e:
        print(f"Complete RAG chain example failed: {e}")
    
    # Example 6: LangGraph
    try:
        example_langgraph()
    except Exception as e:
        print(f"LangGraph example failed: {e}")
    
    # Example 7: Agent with Tools
    try:
        example_agent_with_tools()
    except Exception as e:
        print(f"Agent example failed: {e}")
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
