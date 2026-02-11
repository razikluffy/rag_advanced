"""WebSearch MCP Server - Serper.dev integration for real-time web search."""

import os
from typing import Any, Dict, List

from .base_mcp import BaseMCPServer, MCPResponse


class WebSearchMCPServer(BaseMCPServer):
    """
    MCP server for web search using Serper.dev API.
    Agents call this to search the web for real-time information.
    """

    def __init__(self):
        super().__init__("WebSearchMCPServer")
        self.api_key = os.getenv("SERPER_API_KEY")
        self._search_cache: Dict[str, Dict[str, Any]] = {}
        print(f"[{self.name}] Initialized. API Key configured: {bool(self.api_key)}")

    def call(self, method: str, **params) -> MCPResponse:
        """Handle MCP-style calls."""
        print(f"[{self.name}] Called method: {method} with params: {params.keys()}")
        if method == "search":
            return self._search(**params)
        if method == "health":
            return self._success({"status": "ok", "server": self.name, "api_configured": bool(self.api_key)})
        return self._error(f"Unknown method: {method}")

    def _search(self, query: str, top_k: int = 5, **kwargs) -> MCPResponse:
        """
        Search the web using Serper.dev API.
        Returns formatted search results with title, snippet, and URL.
        """
        print(f"[{self.name}] Searching for: {query}")
        
        # Check cache first
        if query in self._search_cache:
            print(f"[{self.name}] Returning cached result for: {query}")
            return self._success(self._search_cache[query])
        
        # Check if API key is configured
        if not self.api_key:
            print(f"[{self.name}] No API key found. Using LLM fallback.")
            return self._llm_fallback(query, top_k)
        
        try:
            import requests
            
            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "q": query,
                "num": top_k
            }
            
            print(f"[{self.name}] Sending request to Serper API...")
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Format results
            results = []
            for item in data.get("organic", [])[:top_k]:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "url": item.get("link", "")
                })
            
            print(f"[{self.name}] API success. Found {len(results)} results.")
            result_data = {"results": results, "query": query, "total": len(results)}
            self._search_cache[query] = result_data
            return self._success(result_data)
            
        except Exception as e:
            # Fallback to LLM-generated answer if API fails
            print(f"[{self.name}] Web search API failed: {e}. Using LLM fallback.")
            return self._llm_fallback(query, top_k)

    def _llm_fallback(self, query: str, top_k: int = 5) -> MCPResponse:
        """
        Fallback mechanism: Use LLM to generate an informative answer.
        This provides better results than generic simulated data.
        """
        try:
            # Import LLM provider
            import sys
            import os
            # Add parent directory to path to import llm_provider
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from llm_provider import get_llm
            from langchain_core.prompts import ChatPromptTemplate
            
            print(f"[{self.name}] Using LLM to answer: {query}")
            
            prompt = ChatPromptTemplate.from_messages([
                ("system",
                 "You are a knowledgeable assistant with access to general world knowledge. "
                 "Provide a comprehensive, factual answer to the user's question. "
                 "Format your response as if it were a search result snippet (2-3 sentences, factual and informative). "
                 "Do not mention that you're an AI or that you don't have access to real-time data."),
                ("human", "{query}")
            ])
            
            llm = get_llm(temperature=0.3, max_tokens=512)
            chain = prompt | llm
            response = chain.invoke({"query": query})
            answer = response.content if hasattr(response, "content") else str(response)
            
            # Format as search result
            results = [{
                "title": f"Information about: {query}",
                "snippet": answer,
                "url": "https://assistant-generated.local/answer",
                "type": "llm_generated"
            }]
            
            print(f"[{self.name}] LLM fallback generated answer")
            result_data = {"results": results, "query": query, "total": len(results), "is_llm_fallback": True}
            self._search_cache[query] = result_data
            return self._success(result_data)
            
        except Exception as e:
            # Last resort: generic fallback
            print(f"[{self.name}] LLM fallback also failed: {e}. Using generic fallback.")
            results = [{
                "title": f"Search Result for {query}",
                "snippet": f"Unable to retrieve web search results for '{query}'. Please check your internet connection or API configuration.",
                "url": "https://example.com/error",
                "type": "error_fallback"
            }]
            return self._success({"results": results, "query": query, "total": len(results), "is_error": True})
