"""Run the RAG backend. Execute from project root: python run.py"""

import os
import sys
from pathlib import Path

# Run uvicorn from backend directory so imports (rag, mcp_servers, etc.) resolve
backend_dir = Path(__file__).resolve().parent / "backend"
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
