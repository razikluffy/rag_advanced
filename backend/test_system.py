
import unittest
import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add backend directory to sys.path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app, init_app
from mcp_servers.vector_db_mcp import VectorDBMCPServer
from mcp_servers.web_search_mcp import WebSearchMCPServer
from mcp_servers.document_processing_mcp import DocumentProcessingMCPServer

class TestMCPServers(unittest.TestCase):
    def setUp(self):
        # Initialize app for integration tests
        # We might need to mock heavy dependencies if we want pure unit tests
        # but integration tests are better for checking "is working fine"
        # However, init_app loads large models (embedders, etc.), so mocking might be necessary for speed
        # But user wants to verify functionality. Let's try to load but fallback if slow.
        pass

    def test_vector_db_mcp_health(self):
        print("\n[Test] Testing VectorDB MCP Health...")
        server = VectorDBMCPServer()
        response = server.call("health")
        print(f"Response: {response}")
        self.assertTrue(response.success)
        self.assertEqual(response.result["status"], "ok")

    def test_web_search_mcp_health(self):
        print("\n[Test] Testing WebSearch MCP Health...")
        server = WebSearchMCPServer()
        response = server.call("health")
        print(f"Response: {response}")
        self.assertTrue(response.success)
        self.assertEqual(response.result["status"], "ok")

    def test_doc_processing_mcp_health(self):
        print("\n[Test] Testing DocumentProcessing MCP Health...")
        server = DocumentProcessingMCPServer()
        response = server.call("health")
        print(f"Response: {response}")
        self.assertTrue(response.success)
        self.assertEqual(response.result["status"], "ok")

    @patch('requests.post')
    def test_web_search_mcp_search(self, mock_post):
        print("\n[Test] Testing WebSearch MCP Search (Mocked)...")
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "organic": [
                {"title": "Test Result", "snippet": "This is a test snippet.", "link": "http://example.com"}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        server = WebSearchMCPServer()
        # Ensure API key is set for this test or mocked
        with patch.object(server, 'api_key', 'test_key'):
            response = server.call("search", query="test query")
            print(f"Response: {response}")
            self.assertTrue(response.success)
            self.assertIn("results", response.result)
            self.assertEqual(len(response.result["results"]), 1)
            self.assertEqual(response.result["results"][0]["title"], "Test Result")

    def test_web_search_fallback(self):
        print("\n[Test] Testing WebSearch MCP Fallback (No API Key)...")
        server = WebSearchMCPServer()
        # Force no API key
        server.api_key = None
        
        # This might call LLM, so we mocked LLM via patch in a real scenario, 
        # but here let's see if it handles it w/o crashing (it calls _llm_fallback)
        # We'll just check if it returns success (even if content is mocked/simulated)
        # To avoid actual LLM call which might be slow or fail without creds in env, 
        # we can patch _llm_fallback or just let it run if we trust it handles errors gracefully.
        # Let's patch _llm_fallback to verify it's CALLED.
        with patch.object(server, '_llm_fallback') as mock_fallback:
             mock_fallback.return_value = server._success({"results": [], "is_llm_fallback": True})
             response = server.call("search", query="test query")
             self.assertTrue(mock_fallback.called)
             self.assertTrue(response.success)


class TestAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # valuable to test clean state or mock dependencies
        # checking endpoints existence and basic responses
        cls.client = TestClient(app)

    def test_root_endpoint(self):
        # Frontend mount check
        print("\n[Test] Testing Root Endpoint (Frontend Mount)...")
        response = self.client.get("/")
        # If frontend dir exists, it returns 200 (index.html), else 404
        # We can just check it doesn't crash (500)
        print(f"Status: {response.status_code}")
        self.assertNotEqual(response.status_code, 500)

    def test_uploaded_files_endpoint(self):
        print("\n[Test] Testing /uploaded_files Endpoint...")
        response = self.client.get("/uploaded_files")
        print(f"Response: {response.json()}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("files", response.json())

    def test_history_endpoint(self):
        print("\n[Test] Testing /history Endpoint...")
        response = self.client.get("/history")
        print(f"Response: {response.json()}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("history", response.json())

    def test_sessions_endpoint(self):
        print("\n[Test] Testing /sessions Endpoint...")
        response = self.client.get("/sessions")
        print(f"Response: {response.json()}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("sessions", response.json())

    def test_delete_document_endpoint_404(self):
        print("\n[Test] Testing /document/{filename} (Delete Non-existent)...")
        response = self.client.delete("/document/nonexistent_file.pdf")
        print(f"Status: {response.status_code}")
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
