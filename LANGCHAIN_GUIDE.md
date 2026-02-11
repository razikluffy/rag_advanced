# LangChain Integration Guide

This document describes the complete LangChain integration implemented for the RAG system.

## Overview

The RAG system now has full LangChain/LangGraph support with the following components:

1. **LangChain Tools** - MCP servers exposed as LangChain Tools
2. **LangChain Retrievers** - Hybrid, Vector, and Keyword retrievers
3. **LangChain Memory** - Conversation buffer memory with persistence
4. **LCEL Chains** - Composable chains for each agent
5. **LangGraph Workflows** - StateGraph-based agent orchestration

## Quick Start

### Environment Variables

```bash
# Enable all LangChain features
USE_LANGCHAIN=true
USE_LANGCHAIN_MEMORY=true
USE_LANGCHAIN_RETRIEVER=true
USE_LANGCHAIN_GRAPH=true

# Or selectively enable
USE_LANGCHAIN_MEMORY=false  # Use original memory
USE_LANGCHAIN_GRAPH=true    # But use LangGraph
```

### Running the Application

```bash
# With all LangChain features
USE_LANGCHAIN=true python -m backend.main

# Or with specific features
USE_LANGCHAIN_GRAPH=true USE_LANGCHAIN_MEMORY=false python -m backend.main
```

## New Components

### 1. LangChain Tools (`backend/agents/tools.py`)

Tools wrap MCP servers for use in LangChain agents:

```python
from agents.tools import create_tools, VectorDBSearchTool, WebSearchTool

# Create all tools
tools = create_tools(vector_db_mcp, web_search_mcp, doc_processing_mcp)

# Use individually
vector_tool = VectorDBSearchTool(vector_db_mcp=vector_db_mcp)
docs = vector_tool.invoke({"query": "machine learning", "top_k": 5})
```

**Available Tools:**
- `VectorDBSearchTool` - Hybrid search on documents
- `WebSearchTool` - Web search via Serper API
- `DocumentProcessingTool` - Process and index documents

### 2. LangChain Retrievers (`backend/agents/retriever.py`)

Standard LangChain retriever interface:

```python
from agents import create_retriever, HybridRetriever

# Create retriever
retriever = create_retriever(
    vector_db_mcp=vector_db_mcp,
    web_search_mcp=web_search_mcp,
    retriever_type="hybrid",  # or "vector" or "keyword"
    top_k=10,
    use_web_fallback=True
)

# Use like any LangChain retriever
docs = retriever.get_relevant_documents("What is AI?")
```

**Retriever Types:**
- `HybridRetriever` - Vector + BM25 + web fallback
- `VectorRetriever` - Pure semantic search
- `KeywordRetriever` - Pure BM25 keyword search

### 3. LangChain Memory (`backend/agents/memory_langchain.py`)

Full LangChain-compatible memory:

```python
from agents.memory_langchain import create_memory

# Create memory
memory = create_memory(
    memory_key="chat_history",
    return_messages=True,  # Returns LangChain message objects
    k=6,  # Last 6 exchanges
    persist_path="data/conversation_history.json"
)

# Use in chains
memory.add_message("session_123", "user", "Hello")
messages = memory.get_langchain_messages("session_123")

# Load for LangChain
mem_vars = memory.load_memory_variables({"session_id": "session_123"})
chat_history = mem_vars["chat_history"]  # List of BaseMessage
```

### 4. LCEL Chains (`backend/agents/chains.py`)

Runnable chains for each agent:

```python
from agents.chains import (
    create_query_analysis_chain,
    create_relevance_chain,
    create_generation_chain,
    create_rag_chain
)

# Individual chains
qa_chain = create_query_analysis_chain()
result = qa_chain.invoke({"query": "What is Python?"})
# Returns: {"query_intent": "...", "query_type": "...", "query_entities": [...]}

# Complete RAG chain
rag_chain = create_rag_chain(
    retriever=retriever,
    memory=memory,
    reranker=reranker
)
answer = rag_chain.invoke({
    "query": "What is AI?",
    "session_id": "demo"
})
```

### 5. LangGraph Workflow (`backend/graph_langchain.py`)

Proper StateGraph implementation:

```python
from graph_langchain import build_rag_graph, build_simple_rag_graph

# Full workflow with relevance checking
graph = build_rag_graph(vector_db_mcp, web_search_mcp)

# Simple linear workflow (faster)
simple_graph = build_simple_rag_graph(vector_db_mcp, web_search_mcp)

# Agentic RAG with tool use
agentic_graph = build_agentic_rag_graph(vector_db_mcp, web_search_mcp)

# Use the graph
result = graph.invoke({
    "query": "What is machine learning?",
    "session_id": "demo",
    "conversation_history": []
})
```

**Graph Nodes:**
1. `orchestrator` - Query validation and routing
2. `query_analysis` - Extract intent, entities, type
3. `retrieval` - Hybrid search (uses LangChain retriever)
4. `reranking` - BAAI neural re-ranker
5. `relevance_checker` - Evaluate document relevance
6. `web_search` - Web search fallback (if needed)
7. `generation` - LLM answer generation
8. `citation` - Source extraction and formatting

## Updated Agents

### RetrievalAgent (`backend/agents/retrieval_langchain.py`)

Now uses LangChain retriever internally:

```python
from agents.retrieval_langchain import RetrievalAgent

agent = RetrievalAgent(
    vector_db_mcp=vector_db_mcp,
    web_search_mcp=web_search_mcp,
    retriever_type="hybrid"
)

result = agent.invoke({
    "query": "What is AI?",
    "needs_web_search": False
})
# Returns: {"retrieved_chunks": [Document, Document, ...]}
```

## Integration in main.py

The main application now supports both implementations:

```python
# Feature flags
USE_LANGCHAIN = os.getenv("USE_LANGCHAIN", "true").lower() == "true"
USE_LANGCHAIN_MEMORY = os.getenv("USE_LANGCHAIN_MEMORY", "true").lower() == "true"
USE_LANGCHAIN_RETRIEVER = os.getenv("USE_LANGCHAIN_RETRIEVER", "true").lower() == "true"
USE_LANGCHAIN_GRAPH = os.getenv("USE_LANGCHAIN_GRAPH", "true").lower() == "true"

# Initialization creates both sets of components
init_app():
    # Original components
    rag_graph = build_original_graph(...)
    memory = SimpleMemory()
    
    # LangChain components (if enabled)
    if USE_LANGCHAIN_MEMORY:
        lc_memory = create_memory(...)
    if USE_LANGCHAIN_RETRIEVER:
        lc_retriever = HybridRetriever(...)
    if USE_LANGCHAIN:
        lc_tools = create_tools(...)
        lc_chain = create_rag_chain(...)
    if USE_LANGCHAIN_GRAPH:
        rag_graph = build_rag_graph(...)  # LangGraph version
```

## Usage Examples

See `examples_langchain.py` for complete working examples:

```bash
# Run examples
python examples_langchain.py
```

### Example 1: Using Tools

```python
from agents.tools import create_tools

tools = create_tools(vector_db_mcp, web_search_mcp, None)
for tool in tools:
    print(f"{tool.name}: {tool.description}")
```

### Example 2: Using Retrievers

```python
from agents import create_retriever

retriever = create_retriever(
    vector_db_mcp, web_search_mcp, "hybrid"
)
docs = retriever.get_relevant_documents("query")
```

### Example 3: Complete RAG Chain

```python
from agents.chains import create_rag_chain
from agents.memory_langchain import create_memory

memory = create_memory()
rag_chain = create_rag_chain(retriever, memory, reranker)

answer = rag_chain.invoke({
    "query": "What is AI?",
    "session_id": "demo"
})
```

### Example 4: LangGraph Workflow

```python
from graph_langchain import build_rag_graph

graph = build_rag_graph(vector_db_mcp, web_search_mcp)
result = graph.invoke({
    "query": "What is machine learning?",
    "session_id": "demo"
})
```

### Example 5: LangChain Agent

```python
from langchain.agents import create_react_agent, AgentExecutor
from agents.tools import create_tools

tools = create_tools(vector_db_mcp, web_search_mcp, None)
agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

result = executor.invoke({"input": "What is AI?"})
```

## File Structure

```
backend/
├── agents/
│   ├── __init__.py              # Updated exports
│   ├── base_agent.py            # Base class
│   ├── chains.py                # LCEL chains
│   ├── citation.py              # Citation agent
│   ├── generation.py            # Generation agent
│   ├── memory_langchain.py      # LangChain memory
│   ├── orchestrator.py          # Orchestrator agent
│   ├── query_analysis.py        # Query analysis agent
│   ├── relevance_checker.py     # Relevance checker
│   ├── reranking.py             # Re-ranking agent
│   ├── retriever.py             # LangChain retrievers
│   ├── retrieval_langchain.py   # Updated retrieval agent
│   ├── state.py                 # State models
│   └── tools.py                 # LangChain tools
├── graph_langchain.py           # New LangGraph implementation
├── main.py                      # Updated with LangChain integration
└── ...

examples_langchain.py            # Usage examples
LANGCHAIN_GUIDE.md               # This file
```

## Migration Guide

### From Original to LangChain

The original implementation remains functional. To migrate:

1. **Update imports:**
   ```python
   # Old
   from agents.retrieval import RetrievalAgent
   
   # New (uses LangChain retriever)
   from agents.retrieval_langchain import RetrievalAgent
   ```

2. **Use LangChain memory:**
   ```python
   # Old
   from memory import ConversationBufferMemory
   
   # New
   from agents.memory_langchain import ConversationBufferMemory
   ```

3. **Use LangGraph:**
   ```python
   # Old
   from graph import build_rag_graph
   
   # New
   from graph_langchain import build_rag_graph
   ```

### Environment-Based Selection

Keep both implementations and switch via env vars:

```python
if os.getenv("USE_LANGCHAIN") == "true":
    from agents.retrieval_langchain import RetrievalAgent
else:
    from agents.retrieval import RetrievalAgent
```

## Benefits of LangChain Integration

1. **Standard Interface** - Use with any LangChain component
2. **Composability** - Chain components with LCEL (`|` operator)
3. **Tool Use** - Integrate with LangChain agents (ReAct, OpenAI Functions)
4. **Streaming** - Native support for streaming responses
5. **Tracing** - Integration with LangSmith for debugging
6. **Community** - Access to 1000+ LangChain integrations

## Troubleshooting

### Import Errors

```python
# If you get import errors, ensure all dependencies are installed
pip install langchain langgraph langchain-google-genai
```

### Memory Not Persisting

```python
# Ensure persist_path is set
memory = create_memory(persist_path="data/history.json")
```

### Retriever Not Finding Documents

```python
# Check vector store has documents
print(f"Documents in store: {vector_store.count()}")
```

## Performance Considerations

- **LangChain Memory** - Slightly slower due to message conversion
- **LangChain Retriever** - Same performance (wraps same MCP calls)
- **LangGraph** - Adds ~50ms overhead for state management
- **LCEL Chains** - Minimal overhead, mostly syntactic sugar

## Future Enhancements

1. Add LangSmith tracing integration
2. Implement streaming for all chains
3. Add more sophisticated agent types (Plan-and-Execute, BabyAGI)
4. Integrate with LangServe for API deployment
