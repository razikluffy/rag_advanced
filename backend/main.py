"""FastAPI backend - Advanced Multi-Agent RAG with MCP and LangChain."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (parent of backend/)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import tempfile
import uuid
import json
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from rag import (
    parse_document,
    extract_images_ocr,
    semantic_chunk,
    get_embedder,
    create_vector_store,
    create_bm25_index,
    add_chunks_to_store,
    delete_chunks_by_source,
)
from mcp_servers import VectorDBMCPServer, DocumentProcessingMCPServer, WebSearchMCPServer

# Import LangGraph workflow
from graph import build_rag_graph

# Import 6 core agents with LangChain retrievers and components
from memory import ConversationBufferMemory as SimpleMemory
from agents import (
    # Core nodes (used in graph)
    orchestrator_node,
    query_analysis_node,
    retrieval_node,
    reranking_node,
    relevance_checker_node,
    generation_node,
    citation_node,
    # LangChain Integrations
    HybridRetriever,
    create_memory,
    create_rag_chain,
    create_tools,
    # Re-ranker
    BAAIReranker,
)

# Feature flags for LangChain components
USE_LANGCHAIN_MEMORY = os.getenv("USE_LANGCHAIN_MEMORY", "true").lower() == "true"
USE_LANGCHAIN_RETRIEVER = os.getenv("USE_LANGCHAIN_RETRIEVER", "true").lower() == "true"
USE_LANGCHAIN_CHAIN = os.getenv("USE_LANGCHAIN_CHAIN", "false").lower() == "true"

# --- Globals (initialized on startup) ---
embedder = None
vector_store = None
bm25_index = None
vector_db_mcp = None
doc_processing_mcp = None
web_search_mcp = None
rag_graph = None
memory = SimpleMemory()

# LangChain components (optional)
lc_memory = None
lc_retriever = None
lc_tools = None
lc_chain = None

BACKEND_DIR = Path(__file__).resolve().parent
DATA_DIR = BACKEND_DIR.parent / "data"
CHROMA_DIR = DATA_DIR / "chroma_db"
UPLOAD_DIR = DATA_DIR / "uploads"
BM25_INDEX_FILE = DATA_DIR / "bm25_index.json"
CONVERSATION_HISTORY_FILE = DATA_DIR / "conversation_history.json"
UPLOADED_FILES_LIST = DATA_DIR / "uploaded_files.json"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Uploaded files tracking
uploaded_files = []


def init_app():
    """Initialize RAG components, MCP servers, and LangChain integrations."""
    global embedder, vector_store, bm25_index, vector_db_mcp, doc_processing_mcp, web_search_mcp, rag_graph, uploaded_files
    global lc_memory, lc_retriever, lc_tools, lc_chain

    print("[Init] Initializing RAG components...")
    
    # Initialize embedder
    embedder = get_embedder("models/gemini-embedding-001")
    
    # Initialize ChromaDB
    vector_store = create_vector_store(persist_dir=str(CHROMA_DIR))
    
    # Initialize BM25 index
    bm25_index = create_bm25_index()
    
    # Load BM25 index from disk if exists
    if BM25_INDEX_FILE.exists():
        bm25_index.load(str(BM25_INDEX_FILE))
    
    # Load conversation history from disk if exists
    if CONVERSATION_HISTORY_FILE.exists():
        memory.load(str(CONVERSATION_HISTORY_FILE))
    
    # Load uploaded files list
    global uploaded_files
    if UPLOADED_FILES_LIST.exists():
        with open(UPLOADED_FILES_LIST, 'r', encoding='utf-8') as f:
            uploaded_files = json.load(f)

    # Initialize MCP servers
    vector_db_mcp = VectorDBMCPServer(vector_store, bm25_index, embedder)

    doc_processing_mcp = DocumentProcessingMCPServer(
        parser_fn=parse_document,
        ocr_fn=extract_images_ocr,
        chunker_fn=semantic_chunk,
        embedder=embedder,
        vector_store=vector_store,
        bm25_index=bm25_index,
    )

    web_search_mcp = WebSearchMCPServer()
    
    print(f"[Init] MCP servers initialized")

    # Initialize LangChain Memory
    if USE_LANGCHAIN_MEMORY:
        print("[Init] Initializing LangChain memory...")
        lc_memory = create_memory(
            memory_key="chat_history",
            return_messages=True,
            k=6,
            persist_path=str(CONVERSATION_HISTORY_FILE)
        )
    
    # Initialize LangChain Retriever
    if USE_LANGCHAIN_RETRIEVER:
        print("[Init] Initializing LangChain retriever...")
        lc_retriever = HybridRetriever(
            vector_db_mcp=vector_db_mcp,
            web_search_mcp=web_search_mcp,
            top_k=15,
            use_web_fallback=True
        )
    
    # Initialize LangChain Tools
    if USE_LANGCHAIN_CHAIN:
        print("[Init] Initializing LangChain tools...")
        lc_tools = create_tools(vector_db_mcp, web_search_mcp, doc_processing_mcp)
    
    # Initialize LangChain Complete RAG Chain (alternative to graph)
    if USE_LANGCHAIN_CHAIN and lc_retriever:
        print("[Init] Initializing LangChain RAG chain...")
        lc_chain = create_rag_chain(
            retriever=lc_retriever,
            memory=lc_memory,
            reranker=BAAIReranker(),
            temperature=0.4,
            max_tokens=2048
        )
    
    # Build RAG graph
    print("[Init] Building RAG graph...")
    rag_graph = build_rag_graph(vector_db_mcp, web_search_mcp)
    
    print(f"[Init] Complete. ChromaDB: {vector_store.count()} documents")
    print(f"[Init] LangChain features: Memory={USE_LANGCHAIN_MEMORY}, Retriever={USE_LANGCHAIN_RETRIEVER}, Chain={USE_LANGCHAIN_CHAIN}")


# --- API ---
tags_metadata = [
    {
        "name": "Documents",
        "description": "Operations for uploading, listing, and deleting knowledge base documents.",
    },
    {
        "name": "Chat",
        "description": "Primary RAG interface for asking questions.",
    },
    {
        "name": "History",
        "description": "Access conversation history and session management.",
    },
]

app = FastAPI(
    title="Advanced Multi-Agent RAG API",
    description="""
    ## 🚀 Advanced RAG System API
    
    This API provides a multi-agent Retrieval-Augmented Generation (RAG) system with:
    
    *   **Hybrid Search**: Combines ChromaDB (Vector) and BM25 (Keyword).
    *   **Automated Web Search**: Fallback to web search when knowledge base is insufficient.
    *   **Multi-Modal**: Supports PDF (with OCR), TXT, and MD files.
    *   **Agentic Workflow**: Orchestrator -> Retrieval -> Reranking -> Generation.
    
    ### Key Features
    *   Upload and index documents.
    *   Ask questions with citations.
    *   Manage conversation sessions.
    """,
    version="1.0.0",
    openapi_tags=tags_metadata
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    init_app()


# --- Schemas ---
class AskRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class AskResponse(BaseModel):
    answer: str
    citations: List[dict]
    session_id: str


class HistoryResponse(BaseModel):
    session_id: str
    history: List[dict]


# --- Endpoints ---

@app.post("/upload", tags=["Documents"])
async def upload(files: List[UploadFile] = File(...)):
    """Upload PDF/TXT/MD files and add to knowledge base."""
    if not files:
        raise HTTPException(400, "No files provided")

    results = []
    for f in files:
        fn = f.filename or "document"
        ext = Path(fn).suffix.lower()
        if ext not in (".pdf", ".txt", ".md"):
            results.append({"filename": fn, "status": "skipped", "reason": "Unsupported format"})
            continue

        try:
            content = await f.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            parse_result = parse_document(tmp_path, fn)
            docs = parse_result.get("documents", [])
            if isinstance(parse_result, dict) and "documents" not in parse_result:
                docs = [{"content": parse_result.get("text", ""), "metadata": parse_result.get("metadata", {})}]

            ocr_result = extract_images_ocr(tmp_path, fn)
            if ocr_result.get("text"):
                docs.append({"content": ocr_result["text"], "metadata": {"source": fn, "page": "ocr"}})

            chunks = semantic_chunk(docs)
            if chunks:
                add_chunks_to_store(vector_store, bm25_index, chunks, embedder)
                # ChromaDB persists automatically; no save_local needed
                # Save BM25 index
                bm25_index.save(str(BM25_INDEX_FILE))
                
                # Track uploaded file
                uploaded_files.append({
                    "filename": fn,
                    "upload_time": datetime.now().isoformat(),
                    "chunks": len(chunks)
                })
                # Save uploaded files list
                with open(UPLOADED_FILES_LIST, 'w', encoding='utf-8') as f:
                    json.dump(uploaded_files, f, ensure_ascii=False, indent=2)

            Path(tmp_path).unlink(missing_ok=True)
            results.append({"filename": fn, "status": "ok", "chunks": len(chunks)})
        except Exception as e:
            results.append({"filename": fn, "status": "error", "reason": str(e)})

    return {"results": results}


@app.delete("/document/{filename}", tags=["Documents"])
async def delete_document(filename: str):
    """Delete a document and all its chunks from the knowledge base."""
    global uploaded_files
    
    print(f"[Delete] Request to delete document: {filename}")
    
    # 1. Check if file exists in uploaded_files
    file_record = next((f for f in uploaded_files if f["filename"] == filename), None)
    if not file_record:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # 2. Delete chunks from vector store and BM25
        # delete_chunks_by_source is imported from rag
        counts = delete_chunks_by_source(vector_store, bm25_index, filename)
        
        # 3. Remove from uploaded_files list
        uploaded_files = [f for f in uploaded_files if f["filename"] != filename]
        
        # 4. Save updated lists
        # Save BM25 index
        bm25_index.save(str(BM25_INDEX_FILE))
        
        # Save uploaded files list
        with open(UPLOADED_FILES_LIST, 'w', encoding='utf-8') as f:
            json.dump(uploaded_files, f, ensure_ascii=False, indent=2)
            
        return {
            "status": "deleted", 
            "filename": filename, 
            "chunks_deleted": counts
        }
    except Exception as e:
        print(f"[Delete] Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask", response_model=AskResponse, tags=["Chat"])
async def ask(req: AskRequest):
    """Ask a question and get an answer with citations.
    
    Supports both LangGraph workflow and LangChain RAG chain.
    Set USE_LANGCHAIN_CHAIN env var to use the chain instead of graph.
    """
    session_id = req.session_id or str(uuid.uuid4())
    
    # Option 1: Use LangChain RAG Chain if enabled
    if USE_LANGCHAIN_CHAIN and lc_chain and lc_memory:
        print(f"[Ask] Using LangChain RAG chain for session {session_id}")
        
        # Set session in memory
        lc_memory.set_session(session_id)
        
        # Get current history for context
        chat_history = lc_memory.get_langchain_messages(session_id)
        
        try:
            # Invoke the chain
            answer = lc_chain.invoke({
                "query": req.query,
                "session_id": session_id,
                "chat_history": chat_history
            })
            
            # Save to memory
            lc_memory.add_message(session_id, "user", req.query)
            lc_memory.add_message(session_id, "assistant", answer)
            lc_memory.save(str(CONVERSATION_HISTORY_FILE))
            
            return AskResponse(answer=answer, citations=[], session_id=session_id)
            
        except Exception as e:
            print(f"[Ask] LangChain chain failed: {e}, falling back to graph")
    
    # Option 2: Use LangGraph workflow (default)
    history = memory.get(session_id)
    state = {
        "query": req.query,
        "session_id": session_id,
        "conversation_history": history,
        "retrieved_chunks": [],
        "reranked_chunks": [],
        "generated_answer": "",
        "citations": [],
        "final_response": "",
    }

    result = rag_graph.invoke(state)
    final = result.get("final_response", result.get("generated_answer", "No answer generated."))
    citations = result.get("citations", [])

    # Save to memory
    memory.add(session_id, "user", req.query)
    memory.add(session_id, "assistant", final)
    memory.save(str(CONVERSATION_HISTORY_FILE))
    
    # Also save to LangChain memory if available
    if lc_memory:
        lc_memory.add_message(session_id, "user", req.query)
        lc_memory.add_message(session_id, "assistant", final)
        lc_memory.save(str(CONVERSATION_HISTORY_FILE))

    return AskResponse(answer=final, citations=citations, session_id=session_id)


@app.get("/history", response_model=HistoryResponse, tags=["History"])
async def get_history(session_id: Optional[str] = None):
    """Get conversation history for a session."""
    sid = session_id or ""
    return HistoryResponse(session_id=sid, history=memory.get(sid))


@app.get("/sessions", tags=["History"])
async def get_sessions():
    """Get list of all conversation sessions with metadata."""
    sessions = []
    for session_id, history in memory.sessions.items():
        if history:
            first_msg = next((msg for msg in history if msg.get("role") == "user"), None)
            sessions.append({
                "id": session_id,
                "first_message": first_msg.get("content", "")[:50] + "..." if first_msg else "New conversation",
                "message_count": len(history),
                "last_updated": max((msg.get("timestamp", "") for msg in history), default="")
            })
    # Sort by last updated (most recent first)
    sessions.sort(key=lambda x: x.get("last_updated", ""), reverse=True)
    return {"sessions": sessions}


@app.delete("/session/{session_id}", tags=["History"])
async def delete_session(session_id: str):
    """Delete a conversation session."""
    if session_id in memory.sessions:
        del memory.sessions[session_id]
        memory.save(str(CONVERSATION_HISTORY_FILE))
        return {"status": "deleted", "session_id": session_id}
    raise HTTPException(404, "Session not found")


@app.get("/uploaded_files", tags=["Documents"])
async def get_uploaded_files():
    """Get list of uploaded files with metadata."""
    return {"files": uploaded_files}



# --- Serve frontend ---
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
