
import chromadb
from chromadb.config import Settings
import sys
import os

# Setup paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BACKEND_DIR), "data")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma_db")

def fix_deletion():
    print(f"Opening ChromaDB at: {CHROMA_DIR}")
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection("rag_documents")
    
    count_before = collection.count()
    print(f"Total docs before: {count_before}")
    
    # Get all sources
    result = collection.get(include=["metadatas"])
    sources = set()
    for meta in result["metadatas"]:
        if meta and "source" in meta:
            sources.add(meta["source"])
            
    print("\nSources present:")
    target_source = None
    for s in sources:
        print(f" '{s}' (len={len(s)})")
        if "White Simple Invoice.pdf" in s:
            target_source = s
            
    if target_source:
        print(f"\nAttempting to delete exact match: '{target_source}'")
        collection.delete(where={"source": target_source})
        print("Delete command sent.")
        
        count_after = collection.count()
        print(f"Total docs after: {count_after}")
        
        if count_after < count_before:
            print("SUCCESS: Documents deleted.")
        else:
            print("FAILURE: Count did not decrease.")
    else:
        print("\nTarget document not found in sources.")

if __name__ == "__main__":
    fix_deletion()
