
import requests
import json
import sys
import time

# Configuration
API_URL = "http://localhost:8000/api/rag/ask"
SEARCH_URL = "http://localhost:8000/api/rag/search"

def test_rag_query(query):
    print(f"\n{'='*60}")
    print(f"Testing Query: '{query}'")
    print(f"{'='*60}")
    
    payload = {
        "query": query,
        "context_filters": {},
        "top_k": 5
    }
    
    try:
        # 1. Test Retrieval First (Optional debug step)
        print("1. Testing Retrieval...")
        search_res = requests.post(SEARCH_URL, json=payload)
        if search_res.status_code == 200:
            results = search_res.json().get("results", [])
            print(f"   ✓ Retrieved {len(results)} relevant documents")
            for i, doc in enumerate(results[:2]):
                print(f"     - [{doc['source']}] {doc['content'][:100]}...")
        else:
            print(f"   ❌ Retrieval Failed: {search_res.text}")

        # 2. Test Full RAG Generation
        print("\n2. Testing Generation (Gemini)...")
        start_time = time.time()
        response = requests.post(API_URL, json=payload)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Success! (took {duration:.2f}s)")
            print("-" * 60)
            print("🤖 AI Response:")
            print(data.get("answer"))
            print("-" * 60)
            print("📚 Citations:")
            for cite in data.get("citations", []):
                print(f"   Running [Score: {cite['score']:.2f}] - {cite['source']}")
        else:
            print(f"   ❌ RAG Failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to backend. Is the server running?")
        print("   Run: uvicorn app.main:app --reload")

if __name__ == "__main__":
    # Test cases
    queries = [
        "How do I prevent lateral movement using Azure Network Security Groups?",
        "What are the remediation steps for MITRE technique T1078 (Valid Accounts)?",
        "Is it important to enable secure transfer for storage accounts?"
    ]
    
    if len(sys.argv) > 1:
        queries = [sys.argv[1]]
        
    print("Cloud Security RAG System Tester")
    print("Ensuring backend is reachable...")
    
    for q in queries:
        test_rag_query(q)
