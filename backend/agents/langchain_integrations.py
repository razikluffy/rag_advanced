
from typing import Optional, List, Any, Dict
from langchain_core.runnables import Runnable, RunnableLambda, RunnablePassthrough
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import Tool

# Import LLM provider
from llm_provider import get_llm
from agents.reranking import BAAIReranker
from agents.generation import _format_context

# Minimal Retriever Interface to avoid dependency on BaseRetriever if missing
class HybridRetriever(Runnable):
    """
    LangChain Retriever wrapper for VectorDBMCPServer hybrid search.
    """
    def __init__(self, vector_db_mcp, web_search_mcp=None, top_k=15, use_web_fallback=True):
        self.vector_db_mcp = vector_db_mcp
        self.web_search_mcp = web_search_mcp
        self.top_k = top_k
        self.use_web_fallback = use_web_fallback

    def invoke(self, query: str, config: Optional[Any] = None) -> List[Document]:
        # 1. Vector/Hybrid Search
        docs = []
        resp = self.vector_db_mcp.call("hybrid_search", query=query, top_k=self.top_k)
        if resp.success and resp.result:
            for chunk in resp.result.get("chunks", []):
                docs.append(Document(
                    page_content=chunk.get("content", ""),
                    metadata=chunk.get("metadata", {})
                ))
        return docs

class LangChainMemoryAdapter:
    """
    Custom memory adapter that mimics ConversationBufferMemory 
    but supports session management and persistence for main.py checks.
    """
    def __init__(self, memory_key="chat_history", return_messages=True, k=6, persist_path=None):
        self.memory_key = memory_key
        self.return_messages = return_messages
        self.k = k
        self.persist_path = persist_path
        self._sessions = {}
        self._current_session = "default"

    def set_session(self, session_id: str):
        self._current_session = session_id
        if session_id not in self._sessions:
            self._sessions[session_id] = []

    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        
        if role == "user":
            self._sessions[session_id].append(HumanMessage(content=content))
        elif role == "assistant":
            self._sessions[session_id].append(AIMessage(content=content))
        elif role == "system":
            self._sessions[session_id].append(SystemMessage(content=content))

    def get_langchain_messages(self, session_id: str) -> List[Any]:
        """Return history as list of BaseMessage objects."""
        msgs = self._sessions.get(session_id, [])
        # Apply window k (msg pairs) -> 2*k messages
        if self.k > 0:
            return msgs[-2*self.k:]
        return msgs

    def save(self, filepath: str):
        # Persistence is handled by backing store in main.py usually, 
        # but we can implement basic JSON save if needed. 
        # For now, this is a placeholder to satisfy the interface.
        pass

def create_memory(memory_key: str = "chat_history", return_messages: bool = True, k: int = 6, persist_path: str = None):
    return LangChainMemoryAdapter(memory_key, return_messages, k, persist_path)

def create_tools(vector_db_mcp, web_search_mcp, doc_processing_mcp) -> List[Tool]:
    """Wrap MCP servers as LangChain Tools."""
    tools = []
    
    # Vector Search Tool
    def search_func(query: str):
        resp = vector_db_mcp.call("hybrid_search", query=query)
        if resp.success: return str(resp.result)
        return "Error: " + str(resp.error)
        
    tools.append(Tool(
        name="KnowledgeBaseSearch",
        func=search_func,
        description="Search stored documents for information."
    ))
    
    if web_search_mcp:
        def web_func(query: str):
            resp = web_search_mcp.call("search", query=query)
            if resp.success: return str(resp.result)
            return "Error: " + str(resp.error)
            
        tools.append(Tool(
            name="WebSearch",
            func=web_func,
            description="Search the live web for recent information."
        ))

    return tools

def create_rag_chain(retriever, memory, reranker, temperature=0.4, max_tokens=2048) -> Runnable:
    """Create a standard LangChain RAG pipeline."""
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import StrOutputParser
    from operator import itemgetter

    llm = get_llm(temperature=temperature, max_tokens=max_tokens)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer the user's question based on the context below.\n\nContext:\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{query}")
    ])

    def format_docs(docs):
        chunks = [{"content": d.page_content, "metadata": d.metadata} for d in docs]
        return _format_context(chunks)

    # Retrieval chain
    chain = (
        {
            "context": itemgetter("query") | retriever | RunnableLambda(format_docs),
            "query": itemgetter("query"),
            "chat_history": itemgetter("chat_history"),
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain
