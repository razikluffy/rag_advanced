"""Proper LangChain Agent implementations for the RAG system."""

from typing import Any, Dict, List, Optional, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import Runnable, RunnablePassthrough
from pydantic import BaseModel, Field

from llm_provider import get_llm


class QueryAnalysisAgent:
    """LangChain Agent for query analysis with structured output."""
    
    def __init__(self, temperature: float = 0.0, max_tokens: int = 512):
        self.llm = get_llm(temperature=temperature, max_tokens=max_tokens)
        self.parser = JsonOutputParser()
        
        # Define the output schema
        class QueryAnalysisSchema(BaseModel):
            query_intent: str = Field(description="Clear, concise description of user intent")
            query_entities: List[str] = Field(description="List of key entities, terms, and time references")
            query_type: str = Field(description="Type of query: factual, conceptual, comparison, procedural, analytical, exploratory, or other")
        
        self.parser = JsonOutputParser(pydantic_object=QueryAnalysisSchema)
        
        # Create the prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are an expert query analyst. Analyze the user's query deeply to extract intent, entities, and type.\n\n"
             "{format_instructions}"),
            ("human", "{query}"),
        ])
        
        # Create the chain
        self.chain = self.prompt | self.llm | self.parser
    
    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the query analysis agent."""
        query = state.get("query", "")
        if not query:
            return state
        
        try:
            response = self.chain.invoke({
                "query": query,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            return {
                **state,
                "query_intent": response.get("query_intent", ""),
                "query_entities": response.get("query_entities", []),
                "query_type": response.get("query_type", "factual"),
            }
            
        except Exception as e:
            print(f"[Query Analysis Agent] Error: {e}")
            return {
                **state,
                "query_intent": query[:50],
                "query_entities": [],
                "query_type": "factual",
                "error": str(e),
            }


class RelevanceCheckAgent:
    """LangChain Agent for relevance checking with structured output."""
    
    def __init__(self, temperature: float = 0.0, max_tokens: int = 256):
        self.llm = get_llm(temperature=temperature, max_tokens=max_tokens)
        
        # Define the output schema
        class RelevanceResponseSchema(BaseModel):
            relevance_score: int = Field(description="Relevance score from 0 to 10")
            reasoning: str = Field(description="Brief explanation for the score")
        
        self.parser = JsonOutputParser(pydantic_object=RelevanceResponseSchema)
        
        # Create the prompt
        system_msg = (
            "You are a relevance evaluator. Your job is to determine if retrieved document passages "
            "contain information that can answer the user's query.\n\n"
            "Rate relevance from 0-10:\n"
            "- 0-3: Completely irrelevant (different topic entirely, cannot answer query)\n"
            "- 4-6: Partially relevant (related domain but doesn't directly answer the question)\n"
            "- 7-10: Highly relevant (directly answers or provides needed information)\n\n"
            "Be strict: If the passages are about a completely different topic (e.g., query is about 'General Motors' "
            "but passages are about 'fraud analysis'), score should be 0-2.\n\n"
            "{format_instructions}"
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_msg),
            ("human", 
             "User Query: {query}\n\n"
             "Top Retrieved Passages:\n{passages}\n\n"
             "Evaluate relevance.")
        ])
        
        # Create the chain
        self.chain = self.prompt | self.llm | self.parser
    
    def _format_passages(self, chunks: list, max_chunks: int = 3) -> str:
        """Format top chunks for relevance evaluation."""
        out = []
        for i, c in enumerate(chunks[:max_chunks], 1):
            content = c.get("content", "") if isinstance(c, dict) else str(c)
            # Truncate long passages
            if len(content) > 500:
                content = content[:500] + "..."
            meta = c.get("metadata", {}) if isinstance(c, dict) else {}
            src = meta.get("source", "unknown")
            out.append(f"[Passage {i}] (Source: {src})\n{content}")
        return "\n\n".join(out)
    
    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the relevance check agent."""
        query = state.get("query", "")
        chunks = state.get("reranked_chunks", [])
        
        print(f"[Relevance Check Agent] Starting check for query: {query}")
        print(f"[Relevance Check Agent] Number of chunks: {len(chunks)}")
        
        # If no chunks retrieved, definitely need web search
        if not chunks:
            print("[Relevance Check Agent] No chunks found, triggering web search")
            return {
                **state,
                "relevance_score": 0,
                "relevance_reasoning": "No documents retrieved from knowledge base",
                "needs_web_search": True,
            }
        
        # If already flagged for web search (time-sensitive), skip relevance check
        if state.get("needs_web_search"):
            print("[Relevance Check Agent] Already flagged for web search, skipping check")
            return {
                **state,
                "relevance_score": 10,  # Don't override web search decision
                "relevance_reasoning": "Time-sensitive query, using web search",
            }
        
        print("[Relevance Check Agent] Running LLM-based relevance evaluation...")
        passages = self._format_passages(chunks, max_chunks=3)
        
        try:
            response = self.chain.invoke({
                "query": query,
                "passages": passages,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            print(f"[Relevance Check Agent] LLM Response: {response}")
            
            score = response.get("relevance_score", 5)
            reasoning = response.get("reasoning", "")
            
            # Determine if web search is needed (threshold: score < 5)
            needs_web_search = score < 5
            
            print(f"[Relevance Check Agent] Score: {score}/10 | Web Search: {needs_web_search}")
            print(f"[Relevance Check Agent] Reasoning: {reasoning}")
            
            return {
                **state,
                "relevance_score": score,
                "relevance_reasoning": reasoning,
                "needs_web_search": needs_web_search,
            }
            
        except Exception as e:
            print(f"[Relevance Check Agent] Error: {e}")
            # On error, assume documents might be relevant (don't trigger web search)
            return {
                **state,
                "relevance_score": 5,
                "relevance_reasoning": f"Error during relevance check: {e}",
                "needs_web_search": False,
                "error": str(e),
            }


class ToolUsingChain:
    """A LangChain chain that can use tools via tool calling."""
    
    def __init__(self, tools: List[BaseTool], system_prompt: str, temperature: float = 0.0, max_tokens: int = 1024):
        self.llm = get_llm(temperature=temperature, max_tokens=max_tokens)
        self.tools = tools
        
        # Create the prompt with tools
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
        ])
        
        # Create a simple chain (without complex agent execution)
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def invoke(self, input_text: str, chat_history: Optional[List[BaseMessage]] = None) -> str:
        """Execute the tool-using chain."""
        try:
            response = self.chain.invoke({
                "input": input_text,
                "chat_history": chat_history or []
            })
            return response
        except Exception as e:
            print(f"[ToolUsingChain] Error: {e}")
            return f"Error executing chain: {str(e)}"


class RAGAgent:
    """A specialized RAG agent that combines retrieval and generation."""
    
    def __init__(self, retriever: Runnable, temperature: float = 0.4, max_tokens: int = 2048):
        self.llm = get_llm(temperature=temperature, max_tokens=max_tokens)
        self.retriever = retriever
        
        # Create RAG prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Answer the user's question based on the context below.\n\nContext:\n{context}"),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{query}")
        ])
        
        # Create the chain
        from langchain_core.output_parsers import StrOutputParser
        from operator import itemgetter
        
        def format_docs(docs):
            if isinstance(docs, list):
                return "\n\n".join(doc.page_content for doc in docs)
            return str(docs)
        
        self.chain = (
            {
                "context": itemgetter("query") | self.retriever | format_docs,
                "query": itemgetter("query"),
                "chat_history": itemgetter("chat_history"),
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
    
    def invoke(self, query: str, chat_history: Optional[List[BaseMessage]] = None) -> str:
        """Execute the RAG agent."""
        try:
            response = self.chain.invoke({
                "query": query,
                "chat_history": chat_history or []
            })
            return response
        except Exception as e:
            print(f"[RAGAgent] Error: {e}")
            return f"Error generating response: {str(e)}"


# Factory functions for easy agent creation
def create_query_analysis_agent(temperature: float = 0.0, max_tokens: int = 512) -> QueryAnalysisAgent:
    """Create a query analysis agent."""
    return QueryAnalysisAgent(temperature=temperature, max_tokens=max_tokens)


def create_relevance_check_agent(temperature: float = 0.0, max_tokens: int = 256) -> RelevanceCheckAgent:
    """Create a relevance check agent."""
    return RelevanceCheckAgent(temperature=temperature, max_tokens=max_tokens)


def create_tool_using_chain(tools: List[BaseTool], system_prompt: str, 
                          temperature: float = 0.0, max_tokens: int = 1024) -> ToolUsingChain:
    """Create a tool-using chain."""
    return ToolUsingChain(tools, system_prompt, temperature, max_tokens)


def create_rag_agent(retriever: Runnable, temperature: float = 0.4, max_tokens: int = 2048) -> RAGAgent:
    """Create a RAG agent."""
    return RAGAgent(retriever, temperature, max_tokens)
