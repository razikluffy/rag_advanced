# 🚀 RAG_advanced Demo Setup Guide

## 📋 Overview

This guide helps you set up and test the RAG_advanced system with three demo documents:
- **Risk_Fraud_Analyst_Learning_Guide.pdf** - Educational content on fraud analysis
- **White Simple Invoice.pdf** - Business invoice document
- **sample-invoice.pdf** - Sample invoice template

## 🎯 Quick Start

### Option 1: Complete Demo Setup (Recommended)
```bash
python demo_queries.py
```
This will:
1. ✅ Check if server is running
2. 📤 Upload all demo documents
3. 🔍 Test relevant queries for each document
4. 💾 Save results to `demo_results.json`

### Option 2: Upload Documents Only
```bash
python upload_demo_docs.py
```

### Option 3: Test Queries Only
```bash
python test_demo_queries.py
```

## 📤 Document Upload

### Automatic Upload
The demo scripts will automatically upload these files:
- `Risk_Fraud_Analyst_Learning_Guide.pdf`
- `White Simple Invoice.pdf`
- `sample-invoice.pdf`

### Manual Upload
```bash
# Using curl
curl -X POST "http://localhost:8000/upload" \
  -F "file=@Risk_Fraud_Analyst_Learning_Guide.pdf"

curl -X POST "http://localhost:8000/upload" \
  -F "file=@White Simple Invoice.pdf"

curl -X POST "http://localhost:8000/upload" \
  -F "file=@sample-invoice.pdf"
```

## 🔍 Sample Queries

### Fraud Analysis Document
Try these queries with the fraud analysis guide:
- "What are the key steps in fraud analysis?"
- "How do risk analysts identify fraudulent patterns?"
- "What methodologies are used in fraud detection?"
- "Explain the fraud analyst learning process"
- "What are common fraud patterns in financial transactions?"

### Invoice Documents
Try these queries for invoice documents:
- "What is the invoice number from White Simple Invoice?"
- "Who is the issuer of the White Simple Invoice?"
- "What are the payment terms on the White Simple Invoice?"
- "What items or services are billed on the White Simple Invoice?"
- "Show me the sample invoice details"
- "Extract all line items from the sample invoice"

### Combined Queries
Test cross-document understanding:
- "What information do you have about invoices?"
- "Compare the two invoice documents"
- "What do the fraud analysis guide say about financial documents?"

## 📊 Expected Results

### Successful Response Structure
```json
{
  "final_response": "Answer based on retrieved documents...",
  "citations": [
    {
      "source": "document_name.pdf",
      "content": "Relevant excerpt...",
      "score": 0.95
    }
  ],
  "query_intent": "factual",
  "relevance_score": 8
}
```

### Features to Test

1. **Multi-Agent Architecture**
   - Query Analysis Agent extracts intent and entities
   - Retrieval Agent fetches relevant chunks
   - Re-ranking Agent improves relevance with BAAI model
   - Relevance Check Agent evaluates document quality
   - Generation Agent creates contextual answers
   - Citation Agent provides source attribution

2. **Advanced Features**
   - Google Gemini embeddings (gemini-embedding-001)
   - BAAI neural re-ranking
   - Serper web search integration
   - Hybrid vector + BM25 search

3. **Intelligence Capabilities**
   - Document type recognition
   - Entity extraction
   - Intent classification
   - Context-aware responses
   - Source citation

## 🧪 Testing Workflow

### Step 1: Start Server
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Upload Documents
```bash
python upload_demo_docs.py
```

### Step 3: Test Queries
```bash
python test_demo_queries.py
```

### Step 4: Review Results
Check the generated `query_test_results.json` file for:
- Answer accuracy
- Citation quality
- Response relevance
- Agent performance

## 🔧 Configuration

Ensure your `.env` file has:
```env
GOOGLE_API_KEY=your_google_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

## 📈 Performance Metrics

### Success Indicators
- ✅ High relevance scores (>7)
- ✅ Proper citations included
- ✅ Contextually accurate answers
- ✅ Fast response times (<5 seconds)

### Troubleshooting
- ❌ Low relevance scores → Check document quality
- ❌ Missing citations → Verify citation agent
- ❌ Generic answers → Check retrieval and re-ranking
- ❌ Slow responses → Check embedding model

## 🎯 Advanced Testing

### Complex Queries
Test multi-step reasoning:
- "Compare the fraud detection methodologies mentioned in the guide with the invoice payment terms"
- "What would a fraud analyst say about these invoice documents?"
- "Create a risk assessment based on the sample invoice data"

### Cross-Document Analysis
Test document relationships:
- "Do the invoice documents follow standard business practices?"
- "What fraud risks should be considered for these invoices?"
- "Generate a compliance report for the invoice documents"

## 📚 API Endpoints

### Document Management
- `POST /upload` - Upload documents
- `GET /documents` - List uploaded documents
- `DELETE /documents/{source}` - Delete documents

### Query Processing
- `POST /ask` - Main RAG endpoint
- `GET /health` - System health check

### Conversation Management
- `POST /conversations/{session_id}/messages` - Send messages
- `GET /conversations/{session_id}/history` - Get history

## 🎊 Next Steps

After successful demo setup:

1. **Custom Queries** - Create domain-specific questions
2. **Document Expansion** - Add more relevant documents
3. **Performance Tuning** - Adjust agent parameters
4. **Integration Testing** - Test with your actual use case
5. **Production Deployment** - Deploy with Docker

---

## 🎉 Ready to Demo!

Your RAG_advanced system is now ready for comprehensive testing with:
- ✅ Three demo documents uploaded
- ✅ Relevant test queries prepared
- ✅ Automated testing scripts
- ✅ Results collection and analysis

**Start the demo and explore the capabilities! 🚀**
