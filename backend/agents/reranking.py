"""Re-Ranking Agent - Re-ranks retrieved chunks using BAAI neural re-ranker."""

from typing import Any, Dict, List
from sentence_transformers import CrossEncoder


class BAAIReranker:
    """BAAI/bge-reranker-base neural re-ranker for semantic relevance scoring."""
    
    _instance = None  # Singleton to avoid reloading model
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        if self._initialized:
            return
        
        print(f"[BAAI Re-ranker] Loading model: {model_name}...")
        self.model = CrossEncoder(model_name, max_length=512)
        self._initialized = True
        print(f"[BAAI Re-ranker] Model loaded successfully")
    
    def rerank(self, query: str, chunks: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Re-rank chunks using neural cross-encoder.
        
        Args:
            query: User query
            chunks: List of retrieved chunks
            top_k: Number of top chunks to return
            
        Returns:
            Re-ranked chunks with relevance scores
        """
        if not chunks:
            return []
        
        # Prepare query-document pairs
        pairs = [(query, chunk.get("content", "")) for chunk in chunks]
        
        # Get relevance scores from cross-encoder
        scores = self.model.predict(pairs)
        
        # Combine chunks with scores and sort
        scored_chunks = list(zip(chunks, scores))
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        # Add score to metadata for transparency
        reranked = []
        for chunk, score in scored_chunks[:top_k]:
            chunk_copy = chunk.copy()
            if "metadata" not in chunk_copy:
                chunk_copy["metadata"] = {}
            chunk_copy["metadata"]["rerank_score"] = float(score)
            reranked.append(chunk_copy)
        
        return reranked


def reranking_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Re-Ranking Agent: Re-ranks retrieved chunks using BAAI neural re-ranker.
    
    Uses BAAI/bge-reranker-base cross-encoder model for semantic relevance scoring.
    This provides much better accuracy than simple keyword matching.
    """
    chunks = state.get("retrieved_chunks", [])
    query = state.get("query", "")
    
    if not chunks:
        return {**state, "reranked_chunks": []}
    
    print(f"[Re-ranking Agent] Re-ranking {len(chunks)} chunks with BAAI model...")
    
    # Initialize re-ranker (singleton pattern ensures model loads only once)
    reranker = BAAIReranker()
    reranked = reranker.rerank(query, chunks, top_k=10)
    
    print(f"[Re-ranking Agent] Top chunk score: {reranked[0]['metadata'].get('rerank_score', 0):.3f}")
    
    return {**state, "reranked_chunks": reranked}
