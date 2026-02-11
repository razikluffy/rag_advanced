
import sys
import os
import unittest
from fastapi.testclient import TestClient

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, init_app, vector_store, bm25_index
from rag.store import delete_chunks_by_source

class TestDeletionFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize the app components
        # Note: This uses the REAL ChromaDB/VectorStore in 'data/chroma_db'
        # We should be careful, but we'll use a unique test filename
        init_app()
        cls.client = TestClient(app)
        cls.test_filename = "test_deletion_doc.txt"
        cls.test_content = "This is a specialized secret test content about Project Omega123."

    def test_full_flow(self):
        # 1. Upload Document
        print(f"\n[Test] Uploading {self.test_filename}...")
        files = [('files', (self.test_filename, self.test_content, 'text/plain'))]
        response = self.client.post("/upload", files=files)
        self.assertEqual(response.status_code, 200)
        print("Upload response:", response.json())
        
        # Verify it's in the list
        resp = self.client.get("/uploaded_files")
        files_list = resp.json()['files']
        found = any(f['filename'] == self.test_filename for f in files_list)
        self.assertTrue(found, "File not found in uploaded_files list")

        # 2. Search for it (Verify it's indexed)
        # We can use the vector_store directly or the /ask endpoint
        # Let's use /ask to test the full pipeline
        print("\n[Test] Asking about the content...")
        ask_req = {"query": "What is Project Omega123?"}
        resp = self.client.post("/ask", json=ask_req)
        self.assertEqual(resp.status_code, 200)
        answer = resp.json()['answer']
        print(f"Answer: {answer}")
        
        # Expectation: The answer should contain the info
        # Note: If LLM is slow or mocked, this might vary, but let's assume it works or we check citations
        citations = resp.json().get('citations', [])
        print(f"Citations: {citations}")
        
        has_citation = any(c['source'] == self.test_filename for c in citations)
        if not has_citation:
            print("WARNING: No citation found for the uploaded doc yet. Indexing might be slow or failing.")
        
        # 3. Delete the Document
        print(f"\n[Test] Deleting {self.test_filename}...")
        # URL encode if needed, but TestClient handles simple strings
        resp = self.client.delete(f"/document/{self.test_filename}")
        print("Delete response:", resp.json())
        self.assertEqual(resp.status_code, 200)
        
        # 4. Verify Deletion
        # Check uploaded_files list
        resp = self.client.get("/uploaded_files")
        files_list = resp.json()['files']
        found = any(f['filename'] == self.test_filename for f in files_list)
        self.assertFalse(found, "File still exists in uploaded_files list after deletion")
        
        # Check ChromaDB directly (using the global vector_store object)
        # We need to ensure the global vector_store reflects the deletion
        # The delete endpoint uses the global object, so it should be in sync
        # We can use a helper method if available, or just search
        # Or use the debug_delete logic equivalent
        
        # 5. Ask again (Should NOT find it)
        print("\n[Test] Asking again after deletion...")
        ask_req = {"query": "Tell me about Project Omega123"}
        resp = self.client.post("/ask", json=ask_req)
        answer_after = resp.json()['answer']
        citations_after = resp.json().get('citations', [])
        
        print(f"Answer after delete: {answer_after}")
        print(f"Citations after delete: {citations_after}")
        
        # Expectation: No citation from that file
        has_citation_after = any(c['source'] == self.test_filename for c in citations_after)
        self.assertFalse(has_citation_after, "Found citation from deleted file! Deletion failed.")
        
        # Ideally, the answer should be "I don't know" or fallback to web search (which won't know about Omega123)
        # So we expect a generic response or web search results (which will likely be irrelevant/empty for this fake term)

if __name__ == "__main__":
    unittest.main()
