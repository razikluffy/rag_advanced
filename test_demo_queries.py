#!/usr/bin/env python3
"""
Demo Query Testing Script
Tests predefined queries against the RAG system using demo documents.
"""

import json
import requests
from typing import Dict, List


# Predefined queries for each document type
DEMO_QUERIES = {
    "fraud_analysis": [
        "What are the key steps in fraud analysis?",
        "How do risk analysts identify fraudulent patterns?",
        "What methodologies are used in fraud detection?",
        "Explain the fraud analyst learning process",
        "What are common fraud patterns in financial transactions?",
        "How does machine learning help in fraud detection?"
    ],
    "invoice_documents": [
        "What is the invoice number from White Simple Invoice?",
        "Who is the issuer of the White Simple Invoice?",
        "What are the payment terms on the White Simple Invoice?",
        "What items or services are billed on the White Simple Invoice?",
        "What is the total amount due on the White Simple Invoice?",
        "When is the payment due date for the White Simple Invoice?"
    ],
    "sample_invoice": [
        "Show me the sample invoice details",
        "What company issued the sample invoice?",
        "What is the invoice number and date from the sample invoice?",
        "Extract all line items from the sample invoice",
        "What are the tax details on the sample invoice?",
        "Calculate the subtotal and total amounts from the sample invoice"
    ]
}


def test_query(query: str, api_url: str = "http://localhost:8000") -> Dict[str, any]:
    """Test a single query against the RAG system."""
    try:
        response = requests.post(
            f"{api_url}/ask",
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("final_response", result.get("generated_answer", ""))
            
            print(f"🔍 Query: {query}")
            print(f"✅ Answer: {answer[:200]}{'...' if len(answer) > 200 else answer}")
            
            # Extract additional info if available
            if "citations" in result:
                citations = result["citations"]
                if citations:
                    print(f"📚 Sources: {len(citations)} documents cited")
            
            return {
                "query": query,
                "answer": answer,
                "success": True,
                "citations": result.get("citations", [])
            }
        else:
            print(f"❌ Query failed: {query}")
            print(f"   Status: {response.status_code}")
            return {
                "query": query,
                "error": f"HTTP {response.status_code}",
                "success": False
            }
            
    except Exception as e:
        print(f"❌ Query error: {query}")
        print(f"   Error: {e}")
        return {
            "query": query,
            "error": str(e),
            "success": False
        }


def test_query_category(category_name: str, queries: List[str], api_url: str) -> List[Dict[str, any]]:
    """Test a category of queries."""
    print(f"\n📄 Testing {category_name.replace('_', ' ').title()}")
    print("=" * 40)
    
    results = []
    for query in queries:
        result = test_query(query, api_url)
        results.append(result)
        print()
    
    return results


def save_results(all_results: Dict[str, List[Dict]], filename: str = "query_test_results.json"):
    """Save test results to JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\n💾 Results saved to: {filename}")
    except Exception as e:
        print(f"❌ Error saving results: {e}")


def main():
    """Main function to run all demo queries."""
    print("🚀 RAG_advanced Demo Query Testing")
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
    
    # Test all query categories
    all_results = {}
    total_queries = 0
    
    for category_name, queries in DEMO_QUERIES.items():
        results = test_query_category(category_name, queries, api_url)
        all_results[category_name] = results
        total_queries += len(queries)
    
    # Save results
    save_results(all_results)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 QUERY TESTING COMPLETE")
    print("=" * 60)
    
    successful_queries = sum(
        1 for category_results in all_results.values()
        for result in category_results
        if result.get("success", False)
    )
    
    print(f"🔍 Total Queries Tested: {total_queries}")
    print(f"✅ Successful Queries: {successful_queries}")
    print(f"❌ Failed Queries: {total_queries - successful_queries}")
    print(f"📈 Success Rate: {(successful_queries/total_queries)*100:.1f}%")
    
    print("\n📄 Categories Tested:")
    for category_name, results in all_results.items():
        successful = sum(1 for result in results if result.get("success", False))
        total = len(results)
        print(f"   • {category_name.replace('_', ' ').title()}: {successful}/{total} queries")
    
    print(f"\n💾 Detailed results saved to: query_test_results.json")
    print("\n🎯 Next Steps:")
    print("1. Review the query results to verify accuracy")
    print("2. Test additional queries based on your specific needs")
    print("3. Check the citations to verify source attribution")
    print("4. Explore the API documentation at http://localhost:8000/docs")


if __name__ == "__main__":
    main()
