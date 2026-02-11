"""Base MCP Server interface - all MCP servers inherit from this."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class MCPRequest(BaseModel):
    """Standard MCP request structure."""
    method: str
    params: Dict[str, Any] = {}


class MCPResponse(BaseModel):
    """Standard MCP response structure."""
    result: Any = None
    error: Optional[str] = None
    success: bool = True


class BaseMCPServer(ABC):
    """Abstract base class for MCP servers."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def call(self, method: str, **params) -> MCPResponse:
        """Execute an MCP method. All agents call servers via this interface."""
        pass

    def _success(self, result: Any) -> MCPResponse:
        return MCPResponse(result=result, success=True)

    def _error(self, message: str) -> MCPResponse:
        return MCPResponse(error=message, success=False)
