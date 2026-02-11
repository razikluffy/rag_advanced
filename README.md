# RAG_advanced - Advanced Multi-Agent RAG System

A sophisticated Retrieval-Augmented Generation (RAG) system built with LangChain agents, LangGraph orchestration, and FastAPI backend. Features multi-agent architecture, hybrid search, relevance checking, and intelligent query routing.

## 🚀 Features

- **Multi-Agent Architecture**: Query Analysis, Retrieval, Re-ranking, Relevance Checking, Generation, Citation
- **LangChain Integration**: Proper LangChain agents with structured outputs
- **LangGraph Orchestration**: Complex workflow management with conditional routing
- **Google Gemini Embeddings**: Uses `gemini-embedding-001` for high-quality embeddings
- **BAAI Re-ranker**: Advanced neural re-ranking with `BAAI/bge-reranker-base`
- **Serper Web Search**: Real-time web search via Serper.dev API
- **Hybrid Search**: Vector search + BM25 for optimal retrieval
- **Relevance Scoring**: Intelligent document relevance evaluation
- **Citation System**: Automatic source attribution
- **FastAPI Backend**: RESTful API with async support
- **Document Processing**: PDF, OCR, and multi-format support

## 📋 Prerequisites

- Python 3.11 or higher
- Git
- Google AI API key (for Gemini)
- Optional: Ollama for local models

## 🛠️ Installation

### 1. Clone Repository

```bash
git clone <your-repository-url>
cd RAG_advanced
```

### 2. Create Virtual Environment

```bash
# Automated setup (recommended)
python setup_env.py

# Or manual setup
# 1. Create venv
python -m venv venv

# 2. Activate venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
# Copy from .env.example and add your API keys
```

### 3. Install Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### 4. Environment Setup

Create a `.env` file in project root:

```env
# Google AI API Key (Required)
GOOGLE_API_KEY=your_google_api_key_here

# Serper API Key (Required for web search)
SERPER_API_KEY=your_serper_api_key_here

# Ollama Configuration (Optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Vector Database Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db
EMBEDDING_MODEL=models/gemini-embedding-001

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Automated setup (recommended)
python setup_env.py

# Or manual setup
# 1. Create venv
python -m venv venv

# 2. Activate venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
# Copy from .env.example and add your API keys
```

### 2. Start Server

```bash
# Development mode with auto-reload
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Access Web Interface & Upload Documents

After starting the server:

1. **Open Web Interface**: Go to **http://localhost:8000**
2. **Navigate to Upload Section**: Look for "Upload" or "Documents" section
3. **Upload Your PDF Files**: 
   - Click "Choose Files" or "Browse" button
   - Select your PDF documents (invoices, reports, guides, etc.)
   - Click "Upload" to process and index them
4. **Start Asking Questions**: Use the chat interface to query your uploaded documents

### 📤 Demo Documents Available

For testing, the system includes demo documents in the `demo_documents/` folder:
- **White Simple Invoice.pdf** - Sample business invoice
- **sample-invoice.pdf** - Invoice template example
- **Risk_Fraud_Analyst_Learning_Guide.pdf** - Educational fraud analysis guide

### 📋 Upload Your Own Documents

```bash
# Using curl
curl -X POST "http://localhost:8000/upload" \
  -F "file=@your_document.pdf"

# Using web interface
# 1. Open http://localhost:8000
# 2. Go to Upload section
# 3. Select your PDF files
# 4. Click Upload
```

### 🔍 Test the System

```bash
# Using curl
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the invoice number from your uploaded document?"}'

# Using web interface
# 1. Open http://localhost:8000
# 2. Use the chat interface to ask questions about your documents
```

### 4. Demo Setup (Optional)

For testing with demo documents, see:
- **`demo_documents/README.md`** - Demo documents usage guide
- **`WEB_DEMO_INSTRUCTIONS.md`** - Web-based demo instructions

#### Upload Demo Documents
```bash
# Using web interface
# Open http://localhost:8000
# Navigate to Upload section
# Select files from demo_documents/ folder
# Upload and wait for processing

# Using Python scripts
python upload_demo_docs.py
```

#### Test Demo Queries
```bash
# Web interface testing
# Open http://localhost:8000
# Use chat interface with demo documents

# Python testing
python test_demo_queries.py
```

## 📁 Project Structure

```
advanced-rag-system/
├── backend/
│   ├── agents/                 # LangChain agents
│   │   ├── __init__.py
│   │   ├── langchain_agents.py # Core LangChain agent implementations
│   │   ├── agent_wrapper.py   # LangGraph integration wrappers
│   │   ├── query_analysis.py  # Query analysis agent
│   │   ├── retrieval.py      # Document retrieval
│   │   ├── reranking.py      # Document re-ranking
│   │   ├── relevance_checker.py # Relevance evaluation
│   │   ├── generation.py     # Answer generation
│   │   ├── citation.py       # Citation generation
│   │   └── orchestrator.py   # Workflow orchestration
│   ├── graph.py             # LangGraph workflow definition
│   ├── main.py              # FastAPI application
│   ├── llm_provider.py      # LLM provider abstraction
│   ├── memory.py            # Conversation memory
│   ├── mcp_servers.py       # MCP server implementations
│   └── rag.py              # RAG utilities
├── requirements.txt         # Python dependencies
├── setup.py               # Package setup
├── .gitignore            # Git ignore rules
├── .env.example          # Environment template
└── README.md             # This file
```

## 🔧 Configuration

### LLM Providers

The system supports multiple LLM providers:

1. **Google Gemini (Default)**
   - Set `GOOGLE_API_KEY` in your `.env` file
   - Automatically used if available

2. **Ollama (Local)**
   - Install Ollama: https://ollama.ai/
   - Set `OLLAMA_BASE_URL` and `OLLAMA_MODEL` in `.env`
   - Used as fallback when Google API is unavailable

### Vector Database

The system uses ChromaDB for vector storage:

- **Persistence**: Data is stored in `./chroma_db`
- **Embeddings**: Uses sentence-transformers by default
- **Hybrid Search**: Combines vector search with BM25

## 📊 API Endpoints

### Core Endpoints

- `POST /ask` - Ask a question (main RAG endpoint)
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

### Document Management

- `POST /upload` - Upload documents for indexing
- `DELETE /documents/{source}` - Delete documents by source
- `GET /documents` - List indexed documents

### Conversation Management

- `POST /conversations/{session_id}/messages` - Send message
- `GET /conversations/{session_id}/history` - Get conversation history
- `DELETE /conversations/{session_id}` - Clear conversation

## 🧠 Agent Architecture

The system uses a sophisticated multi-agent pipeline:

1. **Orchestrator**: Manages the overall workflow
2. **Query Analysis**: Extracts intent, entities, and query type
3. **Retrieval**: Fetches relevant documents using hybrid search
4. **Re-ranking**: Improves document relevance using BAAI re-ranker
5. **Relevance Check**: Evaluates if documents are sufficient
6. **Generation**: Creates answers using retrieved context
7. **Citation**: Generates proper source citations

## 🔄 Workflow

```
User Query → Orchestrator → Query Analysis → Retrieval → Re-ranking → Relevance Check
                                                              ↓
                                                         Web Search (if needed)
                                                              ↓
                                                         Generation → Citation → Response
```

## 🐳 Docker Support

### Build and Run with Docker

```bash
# Build the image
docker build -t advanced-rag-system .

# Run the container
docker run -p 8000:8000 --env-file .env advanced-rag-system

# Or use docker-compose
docker-compose up -d
```

### Docker Compose

```yaml
version: '3.8'
services:
  rag-system:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - CHROMA_PERSIST_DIRECTORY=/app/data
    volumes:
      - ./data:/app/data
      - ./chroma_db:/app/chroma_db
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=backend tests/

# Run specific test
pytest tests/test_agents.py::test_query_analysis
```

## 📈 Performance Optimization

### Vector Search Optimization

- Use appropriate embedding models for your domain
- Tune `top_k` parameter for retrieval
- Consider document chunking strategies

### Agent Performance

- Adjust LLM temperature for different tasks
- Optimize prompt templates
- Use caching for repeated queries

### Memory Management

- Configure conversation history limits
- Use session-based memory management
- Implement periodic cleanup

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **API Key Issues**: Check `.env` file configuration
3. **Memory Issues**: Increase available RAM or use smaller models
4. **Slow Performance**: Consider using smaller embedding models

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Checks

Monitor system health:

```bash
curl http://localhost:8000/health
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- LangChain for the agent framework
- LangGraph for workflow orchestration
- FastAPI for the web framework
- ChromaDB for vector storage
- Sentence Transformers for embeddings

## 📞 Support

For issues and questions:

- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the troubleshooting section above

---

**Built with ❤️ using LangChain and LangGraph**
- **📄 Advanced Document Processing**: Supports PDFs (with OCR) and text files with semantic chunking.
- **💾 Persistence**: Automatically saves conversation history, uploaded files, and search indexes.
- **🎨 Modern UI**: Beautiful, responsive interface built with vanilla HTML/CSS/JS.

## Technology Stack
- **Orchestration**: LangGraph, LangChain
- **LLM**: Google Gemini
- **Backend**: FastAPI
- **Vector Store**: FAISS
- **Embeddings**: Nomic
- **Frontend**: HTML5, CSS3, JavaScript (No frameworks)

## Setup Instructions

### 1. Clone & Install
```bash
# Clone the repository
git clone <repository-url>
cd cursor_project

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the root directory:
```env
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional (for real web search)
SERPER_API_KEY=your_serper_api_key
```

### 3. Run the Application
```bash
# Start the backend server
uvicorn backend.main:app --reload
```

### 4. Access the UI
Open your browser and navigate to:
http://localhost:8000

## Usage Guide

1. **Upload Documents**: Click "+ Upload Documents" to add PDFs or text files to your knowledge base.
2. **Ask Questions**: Type your query in the chat input.
   - **Document Queries**: "What does the Annual Report say about revenue?"
   - **Web Queries**: "What is the latest news on AI in 2026?"
   - **Hybrid Queries**: "How does our internal fraud policy compare to 2026 industry trends?"
3. **View Files**: Check the "Uploaded Files" sidebar to see your knowledge base.

## Project Structure
```
/backend
  /agents           # LangGraph agents (Orchestrator, Retrieval, etc.)
  /mcp_servers      # Model Context Protocol servers
  /rag              # RAG core (Chunking, Embedding, Store)
  graph.py          # Agent workflow definition
  main.py           # FastAPI application
/frontend
  index.html        # Single-page UI application
/data               # Persisted data (History, Indexes)
```

## License
MIT License
