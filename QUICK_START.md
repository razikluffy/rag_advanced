# 🚀 Quick Start Guide

## One-Command Setup

### Option 1: Automated Setup (Recommended)

```bash
# Clone and setup in one command
git clone <your-repository-url> advanced-rag-system
cd advanced-rag-system
python setup_env.py
```

### Option 2: Manual Setup

```bash
# 1. Clone repository
git clone <your-repository-url> advanced-rag-system
cd advanced-rag-system

# 2. Create virtual environment
python -m venv venv

# 3. Activate environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file
cp .env.example .env
# Edit .env with your API keys

# 6. Start server
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Docker Setup

```bash
# Build and run with Docker
docker-compose up -d

# Or with Ollama (local LLM)
docker-compose --profile ollama up -d
```

## ✅ Verification

Once running, test the system:

```bash
# Health check
curl http://localhost:8000/health

# Test query
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this system?"}'
```

## 📚 Documentation

- **Full Documentation**: [README.md](README.md)
- **API Docs**: http://localhost:8000/docs
- **Project Structure**: See README.md for detailed architecture

## 🔧 Configuration

Required environment variables in `.env`:

```env
GOOGLE_API_KEY=your_google_api_key_here  # REQUIRED
```

Optional variables:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
CHROMA_PERSIST_DIRECTORY=./chroma_db
WEB_SEARCH_API_KEY=your_web_search_api_key
```

## 🐛 Troubleshooting

1. **Import errors**: Run `python setup_env.py` again
2. **API key issues**: Check `.env` file
3. **Port conflicts**: Change port in startup command
4. **Memory issues**: Use smaller models or increase RAM

## 🎯 Next Steps

1. Upload documents via the API
2. Test different query types
3. Explore the API documentation
4. Customize for your use case

---

**Ready to go! 🎉**
