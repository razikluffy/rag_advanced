"""Test script to verify Gemini-Ollama fallback system."""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.llm_provider import get_llm

def test_llm_fallback():
    """Test the LLM fallback system."""
    print("=" * 60)
    print("Testing LLM Fallback System")
    print("=" * 60)
    
    try:
        # Get LLM (will try Gemini first, fallback to Ollama)
        llm = get_llm(temperature=0.3, max_tokens=100)
        print("\n✅ LLM initialized successfully!")
        
        # Test with a simple query
        print("\n" + "-" * 60)
        print("Testing with a simple query...")
        print("-" * 60)
        
        response = llm.invoke("Say 'Hello! I am working correctly.' in one sentence.")
        
        # Extract content
        if hasattr(response, 'content'):
            content = response.content
        else:
            content = str(response)
            
        print(f"\n📝 Response: {content}")
        print("\n✅ LLM is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check if GEMINI_API_KEY is set in .env")
        print("2. OR install Ollama: https://ollama.ai")
        print("3. Pull model: ollama pull llama3.1:8b")
        print("4. Start server: ollama serve")
        return False
    
    print("\n" + "=" * 60)
    print("Test completed successfully! ✅")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_llm_fallback()
    sys.exit(0 if success else 1)
