
import os
import time
from typing import List, Dict, Any

try:
    from pinecone import Pinecone, ServerlessSpec
except ImportError:
    Pinecone = None
    print("Pinecone client not installed.")

_pc = None
_index = None
INDEX_NAME = "cloud-security-rag"

def get_pinecone_client():
    global _pc
    if Pinecone is None:
        print("DEBUG: Pinecone library NOT imported.")
        return None
        
    if _pc is None:
        api_key = os.getenv("PINECONE_API_KEY")
        print(f"DEBUG: PINECONE_API_KEY found: {'Yes' if api_key else 'No'}")
        if not api_key:
            print("Warning: PINECONE_API_KEY not found in environment variables.")
            return None
        try:
            _pc = Pinecone(api_key=api_key)
            print("DEBUG: Pinecone client initialized.")
        except Exception as e:
            print(f"DEBUG: Pinecone client init failed: {e}")
            return None
    return _pc

def get_index():
    global _index
    pc = get_pinecone_client()
    if pc is None: 
        print("DEBUG: get_pinecone_client returned None.")
        return None
        
    if _index is None:
        # separate operations for clarity
        try:
             print(f"DEBUG: Attempting to connect to index '{INDEX_NAME}'...")
             _index = pc.Index(INDEX_NAME)
             print("DEBUG: Index object created.")
        except Exception as e:
            print(f"Error connecting to Pinecone index {INDEX_NAME}: {e}")
            return None
            
    return _index

def upsert_documents(documents: List[Dict[str, Any]], embeddings: List[List[float]]):
    """
    Upsert documents to Pinecone.
    documents: List of dicts with 'id' and 'metadata'.
    embeddings: List of vectors.
    """
    index = get_index()
    if index is None:
        print("Mocking upsert (Pinecone not available)")
        return
    
    vectors = []
    for doc, emb in zip(documents, embeddings):
        vectors.append({
            "id": doc["id"],
            "values": emb,
            "metadata": doc["metadata"]
        })
    
    # Batch upsert could be added here
    index.upsert(vectors=vectors)

def query_vectors(vector: List[float], top_k: int = 5):
    index = get_index()
    if index is None:
        print("Mocking query (Pinecone not available)")
        # Return dummy results for testing UI
        return {
            "matches": [
                {
                    "id": "policy-azure-nsg-001",
                    "score": 0.95,
                    "metadata": {
                        "text": "Azure Storage Accounts should be configured to accept traffic only from authorized virtual networks to minimize exposure to the public internet.",
                        "source": "Azure Policy",
                        "category": "Network Security"
                    }
                },
                {
                    "id": "mitre-t1555-003",
                    "score": 0.88,
                    "metadata": {
                        "text": "Adversaries may acquire credentials from web browsers by reading files specific to the target browser. This can include login data, cookies, and history.",
                        "source": "MITRE ATT&CK",
                        "category": "Credential Access"
                    }
                },
                {
                     "id": "cis-benchmark-3.1",
                     "score": 0.82,
                     "metadata": {
                         "text": "Ensure that Secure Transfer Required is set to Enabled for all Storage Accounts to enforce encryption in transit.",
                         "source": "CIS Benchmark",
                         "category": "Data Protection"
                     }
                }
            ]
        }
    
    return index.query(vector=vector, top_k=top_k, include_metadata=True)
