# 🚀 Demo Usage Guide

## 📁 Demo Documents Folder Structure

```
demo_documents/
├── README.md                    # This file - usage instructions
└── White Simple Invoice.pdf      # Sample invoice document
```

## 🎯 Quick Start Steps

### 1. Start RAG_advanced Server
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Upload Demo Document
```bash
# Method 1: Using curl
curl -X POST "http://localhost:8000/upload" \
  -F "file=@demo_documents/White Simple Invoice.pdf"

# Method 2: Using Python script
python upload_demo_docs.py
```

### 3. Test Sample Queries
```bash
# Basic invoice queries
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the invoice number?"}'

curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Who issued this invoice?"}'

# Advanced analytical queries
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Summarize this invoice document"}'
```

## 📋 Sample Test Queries for Invoice Document

### Basic Information Extraction:
- "What is the invoice number?"
- "Who is the issuer of this invoice?"
- "What is the invoice date?"
- "What are the payment terms?"
- "What is the total amount due?"

### Line Item Analysis:
- "What items or services are billed?"
- "Extract all line items with quantities and prices"
- "What is the unit price for each item?"
- "Are there any discounts applied?"

### Financial Analysis:
- "What is the subtotal before tax?"
- "What is the tax rate and amount?"
- "What is the final total amount?"
- "Calculate the grand total"

### Advanced Queries:
- "Summarize this invoice document"
- "What business insights can you extract?"
- "Are there any unusual charges or patterns?"
- "Generate a payment schedule from this invoice"
- "What compliance information is included?"

## 🔍 Expected RAG_advanced Response Features

### Multi-Agent Processing:
- ✅ **Query Analysis**: Identifies invoice-specific intent
- ✅ **Document Retrieval**: Finds relevant invoice sections
- ✅ **BAAI Re-ranking**: Prioritizes most relevant content
- ✅ **Relevance Checking**: Validates document quality
- ✅ **Answer Generation**: Creates contextual invoice analysis
- ✅ **Citation System**: References specific document sections

### Advanced Technology:
- ✅ **Google Gemini Embeddings**: Superior document understanding
- ✅ **Hybrid Search**: Vector + BM25 optimal retrieval
- ✅ **Serper Web Search**: Real-time fallback capability
- ✅ **Structured Output**: Professional JSON responses

## 📊 Sample Success Response

```json
{
  "final_response": "Based on the White Simple Invoice.pdf document, the invoice number is INV-2024-001, issued by White Corporation Services. The total amount is $1,250.00 with Net 30 payment terms. The document includes 5 line items for consulting services and office supplies.",
  "citations": [
    {
      "source": "White Simple Invoice.pdf",
      "content": "Invoice Number: INV-2024-001, Date: 2024-01-15...",
      "score": 0.96,
      "metadata": {
        "rerank_score": 0.94,
        "page": 1,
        "section": "header"
      }
    }
  ],
  "query_intent": "factual",
  "relevance_score": 9,
  "needs_web_search": false
}
```

## 🎯 Testing Checklist

### ✅ Successful Demo When:
- [ ] Document uploads successfully
- [ ] Queries return accurate, cited answers
- [ ] BAAI re-ranking improves relevance scores (>8)
- [ ] Citations include specific page references
- [ ] Response times under 3 seconds
- [ ] No agent errors or failures

### 🔧 Troubleshooting:
- ❌ **Upload Fails**: Check file path and server connection
- ❌ **Poor Answers**: Verify document processing and embeddings
- ❌ **Missing Citations**: Check citation agent configuration
- ❌ **Slow Responses**: Check embedding model performance

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Complete Guide**: demo_documents/README.md
- **Setup Scripts**: upload_demo_docs.py, test_demo_queries.py

---

## 🎉 Ready for Demo!

Your RAG_advanced system with demo documents is ready to showcase:
- Advanced multi-agent architecture
- Google Gemini + BAAI processing
- Professional invoice analysis
- Intelligent query understanding

**Start with the demo document and test queries! 🚀**
