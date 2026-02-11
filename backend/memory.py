"""Conversation buffer memory for follow-up questions."""

from typing import Any, Dict, List
from collections import defaultdict
from pathlib import Path
from datetime import datetime


class ConversationBufferMemory:
    """In-memory conversation history per session with persistence support."""

    def __init__(self):
        self._store: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    @property
    def sessions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Expose sessions for iteration."""
        return self._store

    def add(self, session_id: str, role: str, content: str) -> None:
        self._store[session_id].append({
            "role": role, 
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def get(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        return self._store[session_id][-limit:]

    def clear(self, session_id: str) -> None:
        self._store[session_id] = []

    def save(self, filepath: str) -> None:
        """Save conversation history to JSON."""
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dict(self._store), f, ensure_ascii=False, indent=2)

    def load(self, filepath: str) -> None:
        """Load conversation history from JSON."""
        import json
        if Path(filepath).exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._store = defaultdict(list, data)
