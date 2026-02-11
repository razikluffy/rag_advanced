"""Retrieval Agent - Calls VectorDB MCP for hybrid search and optionally WebSearch MCP."""

from typing import Any, Dict, Optional


def retrieval_node(state: Dict[str, Any], vector_db_mcp, web_search_mcp: Optional[Any] = None) -> Dict[str, Any]:
    """
    Retrieval Agent: Calls VectorDBMCPServer.hybrid_search to get document chunks.
    Optionally calls WebSearchMCPServer if query needs web search.
    Combines both sources for comprehensive results.
    """
    query = state.get("query", "")
    if not query:
        return {**state, "retrieved_chunks": []}

    # Get document chunks from vector DB (always)
    doc_chunks = []
    resp = vector_db_mcp.call("hybrid_search", query=query, top_k=15)
    if resp.success and resp.result:
        doc_chunks = resp.result.get("chunks", [])

    # Get web search results if needed
    web_chunks = []
    needs_web = state.get("needs_web_search", False)
    print(f"[Retrieval Agent] Needs web search: {needs_web}")
    
    if needs_web:
        if web_search_mcp:
            print(f"[Retrieval Agent] Calling WebSearchMCP...")
            web_resp = web_search_mcp.call("search", query=query, top_k=5)
            if web_resp.success and web_resp.result:
                results = web_resp.result.get("results", [])
                print(f"[Retrieval Agent] Web search returned {len(results)} results")
                for result in results:
                    # Format web results as chunks for consistency
                    web_chunks.append({
                        "content": f"{result['title']}\n\n{result['snippet']}",
                        "metadata": {
                            "source": result["url"],
                            "type": "web_search",
                            "page": "web",
                            "title": result["title"]
                        }
                    })
        else:
            print(f"[Retrieval Agent] WebSearchMCP not injected!")

    # Combine both sources (web results first for recency)
    print(f"[Retrieval Agent] Total chunks: {len(web_chunks)} web + {len(doc_chunks)} docs")
    all_chunks = web_chunks + doc_chunks

    return {**state, "retrieved_chunks": all_chunks}

