"""VectorDB MCP Server - Wraps ChromaDB and BM25 for hybrid search."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_mcp import BaseMCPServer, MCPResponse


class VectorDBMCPServer(BaseMCPServer):
    """
    MCP server for vector DB operations using ChromaDB.
    Agents call this for hybrid search instead of directly using ChromaDB/BM25.
    Delegates to actual RAG components injected at runtime.
    """

    def __init__(self, vector_store=None, bm25_index=None, embedder=None):
        super().__init__("VectorDBMCPServer")
        self._vector_store = vector_store  # ChromaVectorStore
        self._bm25_index = bm25_index
        self._embedder = embedder

    def set_backends(self, vector_store, bm25_index, embedder):
        """Inject RAG backends after they are initialized."""
        self._vector_store = vector_store
        self._bm25_index = bm25_index
        self._embedder = embedder

    def call(self, method: str, **params) -> MCPResponse:
        """Handle MCP-style calls."""
        if method == "vector_search":
            return self._vector_search(**params)
        if method == "keyword_search":
            return self._keyword_search(**params)
        if method == "hybrid_search":
            return self._hybrid_search(**params)
        if method == "add_documents":
            return self._add_documents(**params)
        if method == "health":
            return self._success({"status": "ok", "server": self.name})
        return self._error(f"Unknown method: {method}")

    def _vector_search(
        self, query: str, top_k: int = 10, **kwargs
    ) -> MCPResponse:
        """Vector similarity search via ChromaDB."""
        if not self._vector_store or not self._embedder:
            return self._success({"chunks": [], "scores": []})
        
        try:
            # Generate query embedding
            query_embedding = self._embedder.embed_query(query)
            
            # Search ChromaDB
            chunks = self._vector_store.search(query_embedding, top_k=top_k)
            
            # Extract scores (distances)
            scores = [c.get("distance", 0.0) for c in chunks]
            
            return self._success({"chunks": chunks, "scores": scores})
        except Exception as e:
            print(f"[VectorDB MCP] Vector search error: {e}")
            return self._error(str(e))

    def _keyword_search(
        self, query: str, top_k: int = 10, **kwargs
    ) -> MCPResponse:
        """Keyword search via BM25."""
        if not self._bm25_index:
            return self._success({"chunks": [], "scores": []})
        
        try:
            results = self._bm25_index.search(query, top_k)
            return self._success({"chunks": results, "scores": []})
        except Exception as e:
            print(f"[VectorDB MCP] Keyword search error: {e}")
            return self._error(str(e))

    def _hybrid_search(
        self, query: str, top_k: int = 10, vector_weight: float = 0.7, **kwargs
    ) -> MCPResponse:
        """Combine vector and keyword search, return merged results."""
        vec_resp = self._vector_search(query=query, top_k=top_k * 2)
        kw_resp = self._keyword_search(query=query, top_k=top_k * 2)

        all_chunks: Dict[str, Dict[str, Any]] = {}
        
        # Add vector search results
        if vec_resp.success and vec_resp.result:
            for i, c in enumerate(vec_resp.result.get("chunks", [])):
                key = c.get("content", "")[:100]
                if key not in all_chunks:
                    # ChromaDB returns distance (lower is better), normalize to score (higher is better)
                    distance = vec_resp.result.get("scores", [])[i] if i < len(vec_resp.result.get("scores", [])) else 1.0
                    vec_score = 1.0 / (1.0 + distance)  # Convert distance to similarity score
                    all_chunks[key] = {
                        "chunk": c,
                        "vec_score": vec_score,
                        "kw_score": 0
                    }
        
        # Add keyword search results
        if kw_resp.success and kw_resp.result:
            for i, c in enumerate(kw_resp.result.get("chunks", [])):
                key = c.get("content", "")[:100] if isinstance(c, dict) else str(c)[:100]
                if key not in all_chunks:
                    all_chunks[key] = {
                        "chunk": c if isinstance(c, dict) else {"content": c, "metadata": {}},
                        "vec_score": 0,
                        "kw_score": 1.0 - (i * 0.05)  # Decay score by rank
                    }
                else:
                    all_chunks[key]["kw_score"] = max(
                        all_chunks[key].get("kw_score", 0),
                        1.0 - (i * 0.05)
                    )

        # Weighted score fusion
        ranked = []
        for v in all_chunks.values():
            combined_score = (
                vector_weight * v["vec_score"] +
                (1 - vector_weight) * v.get("kw_score", 0)
            )
            ranked.append((v["chunk"], combined_score))
        
        ranked.sort(key=lambda x: x[1], reverse=True)
        chunks = [r[0] for r in ranked[:top_k]]
        scores = [r[1] for r in ranked[:top_k]]
        
        return self._success({"chunks": chunks, "scores": scores})

    def _add_documents(self, chunks: List[Dict[str, Any]], **kwargs) -> MCPResponse:
        """Add chunks to vector store. Called by DocumentProcessingMCPServer flow."""
        # Actual addition is done in RAG pipeline; this is for MCP interface completeness
        return self._success({"added": len(chunks), "status": "delegated"})
