#!/usr/bin/env python3
"""
Demo Query Generator and Document Upload System
Creates appropriate queries for demo documents and handles upload process.
"""

import os
import json
import requests
from typing import List, Dict, Any
from pathlib import Path


# Demo documents and their characteristics
DEMO_DOCUMENTS = {
    "Risk_Fraud_Analyst_Learning_Guide.pdf": {
        "type": "educational_guide",
        "topics": ["fraud analysis", "risk assessment", "learning methodologies"],
        "potential_queries": [
            "What are the key steps in fraud analysis?",
            "How do risk analysts identify fraudulent patterns?",
            "What methodologies are used in fraud detection?",
            "Explain the fraud analyst learning process",
            "What are common fraud patterns in financial transactions?"
        ]
    },
    "White Simple Invoice.pdf": {
        "type": "business_document",
        "topics": ["invoice", "billing", "business operations"],
        "potential_queries": [
            "What is the invoice number?",
            "Who is the issuer of this invoice?",
            "What are the payment terms on this invoice?",
            "What items or services are billed?",
            "What is the total amount due?",
            "When is the payment due date?"
        ]
    },
    "sample-invoice.pdf": {
        "type": "sample_invoice",
        "topics": ["invoice", "sample document", "template"],
        "potential_queries": [
            "Show me the invoice details",
            "What company issued this invoice?",
            "What is the invoice number and date?",
            "Extract all line items from this invoice",
            "What are the tax details on this invoice?",
            "Calculate the subtotal and total amounts"
        ]
    }
}


def generate_queries_for_document(doc_name: str) -> List[str]:
    """Generate relevant queries for a specific document."""
    doc_info = DEMO_DOCUMENTS.get(doc_name, {})
    return doc_info.get("potential_queries", [])


def generate_all_demo_queries() -> Dict[str, List[str]]:
    """Generate queries for all demo documents."""
    return {
        doc_name: generate_queries_for_document(doc_name)
        for doc_name in DEMO_DOCUMENTS.keys()
    }


def upload_document(file_path: str, api_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """Upload a document to the RAG system."""
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f, 'application/pdf')}
            response = requests.post(f"{api_url}/upload", files=files)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Successfully uploaded {Path(file_path).name}")
                print(f"   Response: {result.get('message', 'Upload successful')}")
                return {"success": True, "response": result}
            else:
                print(f"❌ Failed to upload {Path(file_path).name}")
                print(f"   Status: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
    except Exception as e:
        print(f"❌ Error uploading {Path(file_path).name}: {e}")
        return {"success": False, "error": str(e)}


def upload_all_demo_documents(api_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """Upload all demo documents to the RAG system."""
    results = {}
    
    print("📤 Uploading Demo Documents")
    print("=" * 50)
    
    for doc_name in DEMO_DOCUMENTS.keys():
        file_path = doc_name
        if os.path.exists(file_path):
            result = upload_document(file_path, api_url)
            results[doc_name] = result
        else:
            print(f"⚠️  Document not found: {doc_name}")
            results[doc_name] = {"success": False, "error": "File not found"}
    
    print("=" * 50)
    return results


def test_queries(queries: Dict[str, List[str]], api_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """Test queries against the RAG system."""
    results = {}
    
    print("\n🔍 Testing Demo Queries")
    print("=" * 50)
    
    for doc_name, doc_queries in queries.items():
        print(f"\n📄 Testing queries for: {doc_name}")
        print("-" * 30)
        
        doc_results = []
        for i, query in enumerate(doc_queries, 1):
            print(f"  {i}. Query: {query}")
            
            try:
                response = requests.post(
                    f"{api_url}/ask",
                    json={"query": query},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("final_response", result.get("generated_answer", ""))
                    print(f"     ✅ Answer: {answer[:100]}{'...' if len(answer) > 100 else answer}")
                    
                    doc_results.append({
                        "query": query,
                        "answer": answer,
                        "success": True
                    })
                else:
                    print(f"     ❌ Error: HTTP {response.status_code}")
                    doc_results.append({
                        "query": query,
                        "error": f"HTTP {response.status_code}",
                        "success": False
                    })
                    
            except Exception as e:
                print(f"     ❌ Error: {e}")
                doc_results.append({
                    "query": query,
                    "error": str(e),
                    "success": False
                })
        
        results[doc_name] = doc_results
        print("-" * 30)
    
    return results


def save_results(results: Dict[str, Any], filename: str = "demo_results.json"):
    """Save test results to a file."""
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {filename}")
    except Exception as e:
        print(f"❌ Error saving results: {e}")


def main():
    """Main function to run the complete demo setup."""
    print("🚀 RAG_advanced Demo Document Setup")
    print("=" * 60)
    
    # Check if server is running
    api_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not running. Please start the RAG system first:")
            print("   cd backend")
            print("   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Please start the RAG system first:")
        print("   cd backend")
        print("   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        return
    
    print("✅ Server is running!")
    
    # Step 1: Upload documents
    upload_results = upload_all_demo_documents(api_url)
    
    # Step 2: Generate and test queries
    all_queries = generate_all_demo_queries()
    test_results = test_queries(all_queries, api_url)
    
    # Step 3: Save results
    save_results(test_results)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEMO SETUP COMPLETE")
    print("=" * 60)
    
    successful_uploads = sum(1 for result in upload_results.values() if result.get("success", False))
    total_docs = len(DEMO_DOCUMENTS)
    
    print(f"📤 Documents Uploaded: {successful_uploads}/{total_docs}")
    print(f"🔍 Queries Tested: {sum(len(queries) for queries in test_results.values())}")
    print(f"💾 Results Saved: demo_results.json")
    
    print("\n🎯 Next Steps:")
    print("1. Check the uploaded documents in your RAG system")
    print("2. Review the query results in demo_results.json")
    print("3. Test additional queries based on your specific needs")
    print("4. Explore the API documentation at http://localhost:8000/docs")


if __name__ == "__main__":
    main()
