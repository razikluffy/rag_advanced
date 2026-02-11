"""MCP Servers - Simulated as Python services for agent interaction."""

from .web_search_mcp import WebSearchMCPServer
from .vector_db_mcp import VectorDBMCPServer
from .document_processing_mcp import DocumentProcessingMCPServer

__all__ = [
    "WebSearchMCPServer",
    "VectorDBMCPServer",
    "DocumentProcessingMCPServer",
]
