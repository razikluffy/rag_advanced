#!/usr/bin/env python3
"""
Simple Demo Document Upload Script
Uploads the three demo documents to the RAG system.
"""

import os
import requests
from pathlib import Path


# Demo documents to upload
DEMO_FILES = [
    "Risk_Fraud_Analyst_Learning_Guide.pdf",
    "White Simple Invoice.pdf", 
    "sample-invoice.pdf"
]


def upload_file(file_path: str, api_url: str = "http://localhost:8000"):
    """Upload a single file to the RAG system."""
    try:
        filename = Path(file_path).name
        
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {filename}")
            return False
            
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, 'application/pdf')}
            
            print(f"📤 Uploading {filename}...")
            response = requests.post(f"{api_url}/upload", files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Successfully uploaded {filename}")
                print(f"   Message: {result.get('message', 'Upload successful')}")
                return True
            else:
                print(f"❌ Failed to upload {filename}")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error uploading {filename}: {e}")
        return False


def main():
    """Upload all demo documents."""
    print("🚀 Uploading Demo Documents to RAG_advanced")
    print("=" * 50)
    
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
    
    # Upload each file
    successful_uploads = 0
    for filename in DEMO_FILES:
        if upload_file(filename, api_url):
            successful_uploads += 1
        print()
    
    # Summary
    print("=" * 50)
    print(f"📊 Upload Complete: {successful_uploads}/{len(DEMO_FILES)} files uploaded")
    
    if successful_uploads == len(DEMO_FILES):
        print("🎉 All demo documents uploaded successfully!")
        print("\n🔍 You can now ask questions about:")
        print("   • Fraud analysis and risk assessment")
        print("   • Invoice details and billing information")
        print("   • Sample invoice templates")
        print("\n💡 Try queries like:")
        print("   'What are the key steps in fraud analysis?'")
        print("   'What is the invoice number from the White Simple Invoice?'")
        print("   'Extract all line items from the sample invoice'")
    else:
        print("⚠️  Some uploads failed. Check the error messages above.")
    
    print("\n📚 API Documentation: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
