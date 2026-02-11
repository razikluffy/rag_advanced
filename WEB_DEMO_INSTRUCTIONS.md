# 🌐 Web UI Demo Instructions

## 🎯 Quick Start Guide

### Step 1: Start RAG_advanced Server
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Open Web Interface
Open your browser and go to:
**http://localhost:8000**

## 📤 Upload Documents via Web UI

### Method 1: Using the Upload Page
1. Navigate to **http://localhost:8000**
2. Look for the **Upload** or **Documents** section
3. Click **"Choose Files"** or **"Browse"** button
4. Select your demo documents from the `demo_documents/` folder:
   - `Risk_Fraud_Analyst_Learning_Guide.pdf`
   - `White Simple Invoice.pdf`
   - `sample-invoice.pdf`
5. Click **"Upload"** to process each document
6. Wait for success confirmation

### Method 2: Drag and Drop
1. Open **http://localhost:8000** in your browser
2. Locate the upload area (usually marked with dotted lines or a "+" icon)
3. Drag files directly from `demo_documents/` folder into the upload area
4. Release to upload documents automatically

## 💬 Chat with RAG System

### Starting Conversations
1. On the web page, find the **Chat** or **Ask** section
2. Type your questions in the text input field
3. Press **Enter** or click **"Send"** to submit

### Sample Chat Queries for Demo Documents

#### For Invoice Documents:
- "What is the invoice number from the White Simple Invoice?"
- "Who issued the White Simple Invoice and when?"
- "What are the payment terms shown in the invoice?"
- "Extract all line items with their prices from the invoice"

#### For Fraud Analysis Guide:
- "What are the key steps in fraud analysis according to the guide?"
- "How does the guide explain risk assessment methodologies?"
- "What fraud detection patterns are mentioned in the document?"

#### For Sample Invoice Template:
- "Show me the details from the sample invoice template"
- "What fields are included in this invoice template?"
- "How does this template compare to standard invoices?"

## 🔍 Expected Web UI Features

### Document Management:
- ✅ **File Upload**: Drag-and-drop or file selection interface
- ✅ **Progress Indicators**: Upload status and processing feedback
- ✅ **File List**: View all uploaded documents
- ✅ **Delete Options**: Remove documents by name

### Chat Interface:
- ✅ **Message History**: See previous conversations
- ✅ **Session Management**: Maintain conversation context
- ✅ **Real-time Responses**: Stream answers as they're generated
- ✅ **Citation Display**: See source documents for each answer

### Advanced Features:
- ✅ **Multi-agent Processing**: Query analysis → Retrieval → Re-ranking → Generation
- ✅ **Document Preview**: View uploaded documents in the interface
- ✅ **Search Results**: Highlight relevant passages in responses
- ✅ **Export Options**: Download conversations or results

## 📊 Using Demo Documents

### Upload Process:
1. **Select Files**: Choose from the three demo documents
2. **Upload**: Use the web interface to add them to RAG system
3. **Wait for Processing**: Documents are automatically chunked and embedded
4. **Confirmation**: Get success message when processing completes

### Query Testing:
1. **Start Chat**: Begin conversation in the web interface
2. **Ask Questions**: Use the sample queries provided above
3. **Review Responses**: Check for accurate, cited answers
4. **Follow-up**: Ask related questions to test conversation memory

## 🎯 Expected Results

### Successful Response Features:
- **Fast Answers**: Responses appear in real-time
- **Source Citations**: Each answer shows which documents were used
- **Relevance Scores**: See confidence levels for retrieved content
- **Conversation Context**: System remembers previous questions and answers
- **Multi-turn Dialog**: Natural conversation flow

### Sample Web Interaction:
```
User: What is the invoice number from the White Simple Invoice?

RAG_advanced: Based on the White Simple Invoice.pdf document, the invoice number is 
INV-2024-001, issued by White Corporation Services on January 15, 2024.

📚 Sources:
• White Simple Invoice.pdf (Page 1, Relevance: 96%)
```

## 🔧 Configuration

### Server Settings:
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Required API Keys:
Make sure your `.env` file contains:
```env
GOOGLE_API_KEY=your_google_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

## 🚀 Advanced Demo Workflow

### Complete Demo Session:
1. **Start Server** → Launch RAG_advanced backend
2. **Open Browser** → Navigate to http://localhost:8000
3. **Upload Documents** → Add all 3 demo files via web UI
4. **Test Queries** → Use sample questions for each document type
5. **Verify Features** → Check citations, relevance scores, agent coordination
6. **Explore Capabilities** → Test advanced queries and cross-document analysis

### Professional Demonstration:
- Show multi-agent architecture in action
- Demonstrate Google Gemini embeddings quality
- Highlight BAAI re-ranking improvements
- Test Serper web search integration
- Present professional citation system

## 📈 Success Indicators

### Demo Working When:
- ✅ Documents upload successfully via web interface
- ✅ Chat responses are fast and accurate
- ✅ Citations properly reference uploaded documents
- ✅ Conversation history maintained across sessions
- ✅ All agents coordinate seamlessly

### Troubleshooting Web Issues:
- ❌ **Upload Fails**: Refresh page, check file format, verify server connection
- ❌ **No Chat Response**: Check if server is running, try refreshing
- ❌ **Missing Citations**: Verify document processing completed
- ❌ **Slow Responses**: Check system resources and model performance

## 🎉 Ready for Web Demo!

Your RAG_advanced system includes:
- ✅ **Modern Web Interface** for document upload and chat
- ✅ **Demo Documents** pre-organized and ready to upload
- ✅ **Conversation Memory** for maintaining chat history
- ✅ **Professional UI** for showcasing all RAG capabilities

**Open http://localhost:8000 and start your demo! 🌐**
