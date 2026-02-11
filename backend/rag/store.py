"""Vector store (ChromaDB) and BM25 index."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.config import Settings
from rank_bm25 import BM25Okapi
import numpy as np


class BM25Index:
    """BM25 with metadata - supports incremental corpus via rebuild."""

    def __init__(self):
        self.bm25: Optional[BM25Okapi] = None
        self.chunk_store: List[Dict[str, Any]] = []

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """Add chunks and rebuild BM25 index."""
        self.chunk_store.extend(chunks)
        if self.chunk_store:
            corpus = [c.get("content", "").lower().split() for c in self.chunk_store]
            self.bm25 = BM25Okapi(corpus)

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        if not self.bm25 or not self.chunk_store:
            return []
        tokenized = query.lower().split()
        scores = self.bm25.get_scores(tokenized)
        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            if idx < len(self.chunk_store):
                results.append(self.chunk_store[idx])
        return results

    def save(self, filepath: str) -> None:
        """Save chunk_store to JSON file."""
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.chunk_store, f, ensure_ascii=False, indent=2)

    def load(self, filepath: str) -> None:
        """Load chunk_store from JSON and rebuild BM25 index."""
        import json
        if Path(filepath).exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                self.chunk_store = json.load(f)
            if self.chunk_store:
                corpus = [c.get("content", "").lower().split() for c in self.chunk_store]
                self.bm25 = BM25Okapi(corpus)
    
    def delete_by_source(self, source_filename: str) -> int:
        """Delete all chunks from a specific document source.
        
        Args:
            source_filename: The filename to match in metadata['source']
            
        Returns:
            Number of chunks deleted
        """
        before_count = len(self.chunk_store)
        
        # Filter out chunks matching the source
        self.chunk_store = [
            chunk for chunk in self.chunk_store
            if chunk.get("metadata", {}).get("source") != source_filename
        ]
        
        after_count = len(self.chunk_store)
        deleted = before_count - after_count
        
        # Rebuild BM25 index with remaining chunks
        if self.chunk_store:
            corpus = [c.get("content", "").lower().split() for c in self.chunk_store]
            self.bm25 = BM25Okapi(corpus)
        else:
            self.bm25 = None
        
        print(f"[BM25] Deleted {deleted} chunks from '{source_filename}'. Remaining: {after_count}")
        return deleted


class ChromaVectorStore:
    """ChromaDB-based vector store with automatic persistence."""
    
    def __init__(self, persist_dir: str = "data/chroma_db", collection_name: str = "rag_documents"):
        """Initialize ChromaDB with persistent storage."""
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        print(f"[ChromaDB] Initialized. Collection: {collection_name}, Documents: {self.collection.count()}")
    
    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> None:
        """Add chunks with embeddings to ChromaDB."""
        if not chunks:
            return
        
        # Generate unique IDs
        import hashlib
        ids = []
        for i, chunk in enumerate(chunks):
            content_hash = hashlib.md5(chunk["content"].encode()).hexdigest()[:8]
            ids.append(f"chunk_{i}_{content_hash}")
        
        documents = [c["content"] for c in chunks]
        metadatas = [c.get("metadata", {}) for c in chunks]
        
        # ChromaDB requires metadata values to be str, int, float, or bool
        # Convert any other types to strings
        clean_metadatas = []
        for meta in metadatas:
            clean_meta = {}
            for k, v in meta.items():
                if isinstance(v, (str, int, float, bool)):
                    clean_meta[k] = v
                else:
                    clean_meta[k] = str(v)
            clean_metadatas.append(clean_meta)
        
        try:
            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=clean_metadatas
            )
            print(f"[ChromaDB] Added {len(chunks)} chunks. Total: {self.collection.count()}")
        except Exception as e:
            print(f"[ChromaDB] Error adding chunks: {e}")
    
    def search(self, query_embedding: List[float], top_k: int = 10, filter_metadata: dict = None) -> List[Dict[str, Any]]:
        """Vector similarity search."""
        if self.collection.count() == 0:
            return []
        
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, self.collection.count()),
                where=filter_metadata
            )
            
            chunks = []
            for i, doc in enumerate(results['documents'][0]):
                chunks.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0.0
                })
            return chunks
        except Exception as e:
            print(f"[ChromaDB] Search error: {e}")
            return []
    
    def count(self) -> int:
        """Return number of documents in collection."""
        return self.collection.count()
    
    def reset(self) -> None:
        """Clear all documents from collection."""
        self.client.reset()
        print("[ChromaDB] Collection reset")
    
    def delete_by_source(self, source_filename: str) -> int:
        """Delete all chunks from a specific document source.
        
        Args:
            source_filename: The filename to match in metadata['source']
            
        Returns:
            Number of chunks deleted
        """
        # Get current count
        before_count = self.collection.count()
        
        # Verify chunks exist for this source before trying to delete
        # This is expensive but safer for debugging
        existing = self.collection.get(where={"source": source_filename}, include=["metadatas"])
        params_count = len(existing["ids"])
        
        print(f"[ChromaDB] Deleting chunks for source '{source_filename}'. Found {params_count} chunks to delete.")
        
        if params_count == 0:
            print(f"[ChromaDB] No chunks found for '{source_filename}'")
            return 0

        # Delete by metadata filter
        self.collection.delete(
            where={"source": source_filename}
        )
        
        # Get new count
        after_count = self.collection.count()
        deleted = before_count - after_count
        
        # Double check if any remain
        remaining = self.collection.get(where={"source": source_filename}, include=["metadatas"])
        if len(remaining["ids"]) > 0:
             print(f"[ChromaDB] ⚠️ WARNING: {len(remaining['ids'])} chunks still remain after deletion!")
             # Retry?
             self.collection.delete(where={"source": source_filename})

        print(f"[ChromaDB] Deleted {deleted} chunks from '{source_filename}'. Remaining total: {after_count}")
        return deleted


def create_vector_store(persist_dir: Optional[str] = None) -> ChromaVectorStore:
    """Create or load ChromaDB vector store."""
    persist_path = persist_dir if persist_dir else "data/chroma_db"
    return ChromaVectorStore(persist_dir=persist_path)


def create_bm25_index(documents: Optional[List[Dict[str, Any]]] = None) -> BM25Index:
    """Create BM25 index."""
    idx = BM25Index()
    if documents:
        idx.add_chunks(documents)
    return idx


def add_chunks_to_store(
    vector_store: ChromaVectorStore,
    bm25_index: BM25Index,
    chunks: List[Dict[str, Any]],
    embedder,
) -> None:
    """Add chunks to ChromaDB and BM25."""
    if not chunks:
        return
    
    # Generate embeddings for all chunks
    texts = [c.get("content", "") for c in chunks]
    embeddings = embedder.embed_documents(texts)
    
    # Add to ChromaDB
    vector_store.add_chunks(chunks, embeddings)
    
    # Add to BM25
    bm25_index.add_chunks(chunks)


def delete_chunks_by_source(
    vector_store: ChromaVectorStore,
    bm25_index: BM25Index,
    source_filename: str,
) -> Dict[str, int]:
    """Delete all chunks from a specific document source.
    
    Args:
        vector_store: ChromaDB vector store
        bm25_index: BM25 index
        source_filename: The filename to match
        
    Returns:
        Dictionary with deletion counts: {'vector_store': N, 'bm25': M}
    """
    vector_deleted = vector_store.delete_by_source(source_filename)
    bm25_deleted = bm25_index.delete_by_source(source_filename)
    
    return {
        "vector_store": vector_deleted,
        "bm25": bm25_deleted
    }
