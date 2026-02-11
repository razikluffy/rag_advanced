# 📁 Demo Documents Collection

This folder contains sample documents for testing the RAG_advanced system.

## 📋 Available Documents

### 1. White Simple Invoice.pdf
- **Type**: Business Invoice Document
- **Content**: Standard business invoice with line items, totals, and payment terms
- **Use For**: Testing invoice analysis, extraction, and business document processing

### 2. [Additional Documents]
*Note: The other demo documents (Risk_Fraud_Analyst_Learning_Guide.pdf and sample-invoice.pdf) were referenced but not found in the current directory. You can add your own documents here for testing.*

## 🎯 How to Use These Documents

### Step 1: Upload Documents
Use the RAG_advanced upload endpoint to add these documents:

```bash
# Using curl
curl -X POST "http://localhost:8000/upload" \
  -F "file=@demo_documents/White Simple Invoice.pdf"

# Using Python
import requests

with open("demo_documents/White Simple Invoice.pdf", 'rb') as f:
    files = {'file': ('White Simple Invoice.pdf', f, 'application/pdf')}
    response = requests.post("http://localhost:8000/upload", files=files)
```

### Step 2: Test Queries
Try these sample queries:

#### Basic Invoice Queries:
- "What is the invoice number?"
- "Who issued this invoice?"
- "What are the payment terms?"
- "What is the total amount due?"
- "Extract all line items from this invoice"

#### Analytical Queries:
- "Summarize this invoice document"
- "What business insights can you extract from this invoice?"
- "Are there any unusual charges or patterns?"
- "What tax rate is applied?"

#### Advanced Queries:
- "Compare this invoice with standard business practices"
- "What compliance issues should be noted?"
- "Generate a payment schedule from this invoice"

## 🔍 Expected RAG_advanced Features

When testing with these documents, you should see:

### Multi-Agent Processing:
- ✅ **Query Analysis Agent**: Extracts intent (invoice analysis, data extraction)
- ✅ **Retrieval Agent**: Finds relevant invoice sections
- ✅ **Re-ranking Agent**: BAAI model improves relevance
- ✅ **Relevance Check Agent**: Validates document quality
- ✅ **Generation Agent**: Creates contextual answers
- ✅ **Citation Agent**: Provides source attribution

### Advanced Features:
- ✅ **Google Gemini Embeddings**: High-quality document understanding
- ✅ **Hybrid Search**: Vector + BM25 for optimal retrieval
- ✅ **Serper Web Search**: Real-time information fallback
- ✅ **Structured Output**: Properly formatted responses with citations

## 📊 Sample Expected Response

```json
{
  "final_response": "Based on the White Simple Invoice.pdf document, the invoice number is INV-2024-001, issued by White Corporation. The total amount due is $1,250.00 with payment terms of Net 30 days. The document contains 5 line items for consulting services and office supplies.",
  "citations": [
    {
      "source": "White Simple Invoice.pdf",
      "content": "Invoice Number: INV-2024-001...",
      "score": 0.95,
      "metadata": {
        "rerank_score": 0.92,
        "page": 1
      }
    }
  ],
  "query_intent": "factual",
  "relevance_score": 9,
  "needs_web_search": false
}
```

## 🚀 Quick Start

1. **Start RAG_advanced Server**:
   ```bash
   cd backend
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Upload This Document**:
   ```bash
   curl -X POST "http://localhost:8000/upload" \
     -F "file=@demo_documents/White Simple Invoice.pdf"
   ```

3. **Test Sample Queries**:
   ```bash
   curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the invoice number?"}'
   ```

## 📚 Adding More Documents

To add your own documents for testing:

1. **Copy files to this folder**:
   ```bash
   cp your_document.pdf demo_documents/
   ```

2. **Upload via API**:
   ```bash
   curl -X POST "http://localhost:8000/upload" \
     -F "file=@demo_documents/your_document.pdf"
   ```

3. **Test with relevant queries** for your specific document type

## 🔧 Configuration Notes

Make sure your `.env` file contains:
```env
GOOGLE_API_KEY=your_google_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

---

## 🎯 Ready for Testing!

The RAG_advanced system is now ready to demonstrate:
- Multi-agent document processing
- Advanced embedding and re-ranking
- Intelligent query understanding
- Professional citation system

**Upload your documents and start testing! 🚀**
