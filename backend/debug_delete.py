
import chromadb
from chromadb.config import Settings
import sys
import os

# Setup paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BACKEND_DIR), "data")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma_db")

print(f"Checking ChromaDB at: {CHROMA_DIR}")

def list_documents():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        collection = client.get_collection("rag_documents")
    except Exception as e:
        print(f"Collection not found: {e}")
        return

    count = collection.count()
    print(f"Total documents: {count}")
    
    if count > 0:
        result = collection.get(include=["metadatas", "documents"])
        sources = set()
        for meta in result["metadatas"]:
            if meta and "source" in meta:
                sources.add(meta["source"])
        
        print("\nUnique Sources found in DB:")
        for s in sources:
            print(f" - {s}")
            
        # Check specific file if needed
        # print("\nSample chunks:")
        # for i in range(min(3, count)):
        #     print(f"Chunk {i}: {result['documents'][i][:50]}... | Meta: {result['metadatas'][i]}")

if __name__ == "__main__":
    list_documents()
