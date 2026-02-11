"""Semantic chunking for documents."""

import re
from typing import Any, Dict, List

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    HAS_RECURSIVE = True
except ImportError:
    HAS_RECURSIVE = False


def semantic_chunk(documents: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
    """
    Apply semantic-style chunking to documents.
    Uses recursive split by meaning boundaries (paragraphs, sentences).
    Each doc: { content: str, metadata: dict }
    Returns list of { content: str, metadata: dict }
    """
    if not documents:
        return []

    if HAS_RECURSIVE:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=64,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
    else:
        splitter = None

    chunks: List[Dict[str, Any]] = []
    for doc in documents:
        content = doc.get("content", "")
        metadata = doc.get("metadata", {})
        if not content or not isinstance(content, str):
            continue

        if splitter:
            sub_chunks = splitter.split_text(content)
        else:
            sub_chunks = _fallback_split(content)

        for c in sub_chunks:
            if c.strip():
                chunks.append({"content": c.strip(), "metadata": dict(metadata)})

    return chunks


def _fallback_split(text: str, max_chunk: int = 512, overlap: int = 64) -> List[str]:
    """Paragraph/sentence-based fallback chunking."""
    paragraphs = re.split(r"\n\s*\n", text)
    chunks: List[str] = []
    current: List[str] = []
    current_len = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if current_len + len(para) + 1 <= max_chunk:
            current.append(para)
            current_len += len(para) + 1
        else:
            if current:
                chunks.append("\n\n".join(current))
            current = [para]
            current_len = len(para)
            if current_len > max_chunk:
                words = para.split()
                for i in range(0, len(words), max(1, max_chunk // 5)):
                    seg = " ".join(words[i : i + max(1, max_chunk // 5)])
                    if seg:
                        chunks.append(seg)
                current = []
                current_len = 0

    if current:
        chunks.append("\n\n".join(current))
    return chunks
