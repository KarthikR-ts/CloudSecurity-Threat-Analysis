
import os
import sys
from pathlib import Path
from pinecone import Pinecone, ServerlessSpec

# Add backend key to path 
sys.path.append(str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

def init_pinecone():
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("Error: PINECONE_API_KEY not found.")
        return

    pc = Pinecone(api_key=api_key)
    index_name = "cloud-security-rag"
    
    # Check if index exists
    existing_indexes = pc.list_indexes().names()
    
    if index_name not in existing_indexes:
        print(f"Creating index '{index_name}'...")
        try:
            pc.create_index(
                name=index_name,
                dimension=384, # distinct for all-MiniLM-L6-v2
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            print(f"Index '{index_name}' created successfully.")
        except Exception as e:
            print(f"Error creating index: {e}")
            # Try generic serverless if region fails? 
            # Usually us-east-1 is the default free tier region.
    else:
        print(f"Index '{index_name}' already exists.")

if __name__ == "__main__":
    init_pinecone()
