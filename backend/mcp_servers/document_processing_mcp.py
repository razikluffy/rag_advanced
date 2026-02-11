"""DocumentProcessing MCP Server - Handles PDF/TXT/MD parsing, OCR, chunking."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_mcp import BaseMCPServer, MCPResponse


class DocumentProcessingMCPServer(BaseMCPServer):
    """
    Simulated MCP server for document processing.
    Agents/delegates call this for parsing, OCR, and chunking.
    Actual logic is delegated to RAG pipeline functions injected at runtime.
    """

    def __init__(
        self,
        parser_fn=None,
        ocr_fn=None,
        chunker_fn=None,
        embedder=None,
        vector_store=None,
        bm25_index=None,
    ):
        super().__init__("DocumentProcessingMCPServer")
        self._parser_fn = parser_fn
        self._ocr_fn = ocr_fn
        self._chunker_fn = chunker_fn
        self._embedder = embedder
        self._vector_store = vector_store
        self._bm25_index = bm25_index

    def set_backends(
        self,
        parser_fn=None,
        ocr_fn=None,
        chunker_fn=None,
        embedder=None,
        vector_store=None,
        bm25_index=None,
    ):
        """Inject processing backends."""
        if parser_fn is not None:
            self._parser_fn = parser_fn
        if ocr_fn is not None:
            self._ocr_fn = ocr_fn
        if chunker_fn is not None:
            self._chunker_fn = chunker_fn
        if embedder is not None:
            self._embedder = embedder
        if vector_store is not None:
            self._vector_store = vector_store
        if bm25_index is not None:
            self._bm25_index = bm25_index

    def call(self, method: str, **params) -> MCPResponse:
        """Handle MCP-style calls."""
        if method == "parse_document":
            return self._parse_document(**params)
        if method == "extract_images_ocr":
            return self._extract_images_ocr(**params)
        if method == "chunk_documents":
            return self._chunk_documents(**params)
        if method == "process_and_store":
            return self._process_and_store(**params)
        if method == "health":
            return self._success({"status": "ok", "server": self.name})
        return self._error(f"Unknown method: {method}")

    def _parse_document(self, file_path: str, filename: str, **kwargs) -> MCPResponse:
        """Parse PDF/TXT/MD and return extracted text + metadata."""
        if not self._parser_fn:
            return self._error("Parser not configured")
        try:
            result = self._parser_fn(file_path, filename)
            return self._success(result)
        except Exception as e:
            return self._error(str(e))

    def _extract_images_ocr(self, file_path: str, filename: str, **kwargs) -> MCPResponse:
        """Extract images from PDF and run OCR."""
        if not self._ocr_fn:
            return self._success({"text": "", "images_processed": 0})
        try:
            result = self._ocr_fn(file_path, filename)
            return self._success(result)
        except Exception as e:
            return self._error(str(e))

    def _chunk_documents(
        self, documents: List[Dict[str, Any]], **kwargs
    ) -> MCPResponse:
        """Apply semantic chunking to documents."""
        if not self._chunker_fn:
            return self._error("Chunker not configured")
        try:
            chunks = self._chunker_fn(documents)
            return self._success({"chunks": chunks})
        except Exception as e:
            return self._error(str(e))

    def _process_and_store(
        self,
        file_path: str,
        filename: str,
        **kwargs
    ) -> MCPResponse:
        """
        Full pipeline: parse -> OCR -> chunk -> embed -> store.
        Delegates to backend functions.
        """
        if not all([self._parser_fn, self._chunker_fn, self._embedder, self._vector_store, self._bm25_index]):
            return self._error("Processing pipeline not fully configured")
        try:
            # Parse
            parse_result = self._parser_fn(file_path, filename)
            docs = parse_result.get("documents", [parse_result])
            if isinstance(docs, dict):
                docs = [{"content": parse_result.get("text", ""), "metadata": parse_result.get("metadata", {})}]

            # OCR for PDF images (if available)
            if self._ocr_fn:
                ocr_result = self._ocr_fn(file_path, filename)
                ocr_text = ocr_result.get("text", "")
                if ocr_text:
                    docs.append({"content": ocr_text, "metadata": {"source": filename, "page": "ocr"}})

            # Chunk
            chunks = self._chunker_fn(docs)
            if not chunks:
                return self._success({"chunks_added": 0, "filename": filename})

            # Embed and store (done by RAG store module)
            # This MCP returns chunks; actual storage happens in upload flow
            return self._success({
                "chunks": chunks,
                "chunk_count": len(chunks),
                "filename": filename,
            })
        except Exception as e:
            return self._error(str(e))
