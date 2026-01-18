
import requests
import json
import gzip
import io
import os
import sys

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.embeddings import generate_embedding
from app.rag.vector_db import upsert_documents

# NVD Feeds (Using 2024 and 2025 for relevance)
NVD_URLS = [
    "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-2024.json.gz",
    "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-2023.json.gz" # 2025 might be too empty early in year
]

def download_and_ingest():
    processed_count = 0
    documents = []
    
    print("🚀 Starting CVE Ingestion...")
    
    for url in NVD_URLS:
        print(f"📥 Downloading {url}...")
        try:
            # Add User-Agent to avoid 403 Forbidden
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers, stream=True)
            if response.status_code != 200:
                print(f"❌ Failed to download {url}. Status: {response.status_code}, Reason: {response.reason}")
                continue

            print("   Decoding GZIP...")
            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
                data = json.load(f)
                cve_items = data.get("CVE_Items", [])
            
            print(f"   Found {len(cve_items)} CVEs. Filtering for HIGH/CRITICAL...")
                    
            for item in cve_items:
                # Extract basic info
                try:
                    cve_id = item['cve']['CVE_data_meta']['ID']
                    description = item['cve']['description']['description_data'][0]['value']
                    
                    # Check Severity (V3)
                    impact = item.get('impact', {}).get('baseMetricV3', {})
                    if impact:
                        severity = impact.get('cvssV3', {}).get('baseSeverity', 'UNKNOWN')
                        score = impact.get('cvssV3', {}).get('baseScore', 0)
                        
                        # Filter: Only High/Critical
                        if severity in ['HIGH', 'CRITICAL']:
                            
                            text = f"{cve_id} ({severity}): {description}"
                            
                            doc = {
                                "id": cve_id.lower(),
                                "text": text,
                                "metadata": {
                                    "source": "NVD CVE",
                                    "severity": severity,
                                    "score": score,
                                    "year": url.split("-")[-1].split(".")[0]
                                }
                            }
                            documents.append(doc)
                except Exception as e:
                    continue
        
        except Exception as e:
            print(f"❌ Error processing {url}: {e}")

    print(f"✅ Filtered down to {len(documents)} High/Critical CVEs.")
    
    # Limit to 5000 to avoid hitting free tier limits instantly if too many
    # Pinecone Free Tier allows ~100k vectors, so 5k is fine.
    MAX_DOCS = 5000
    if len(documents) > MAX_DOCS:
        print(f"⚠️ Capping at {MAX_DOCS} for demonstration speed...")
        documents = documents[:MAX_DOCS]

    # Batch Process
    batch_size = 50
    total_batches = (len(documents) + batch_size - 1) // batch_size
    
    print(f"💾 Upserting in {total_batches} batches...")
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        
        # Generate embeddings
        # Note: In production, batch embedding is faster. 
        # Here we loop for simplicity with our existing function
        
        # Prepare lists for upsert_documents
        batch_docs = []
        batch_embeddings = []
        
        for doc in batch:
            emb = generate_embedding(doc['text'])
            batch_embeddings.append(emb)
            
            batch_docs.append({
                "id": doc['id'],
                "metadata": {
                    "text": doc['text'],
                    "source": doc['metadata']['source'],
                    "severity": doc['metadata']['severity'],
                    "score": float(doc['metadata']['score']),
                    "year": doc['metadata']['year']
                }
            })
            
        # Upsert using the correct signature: documents, embeddings
        upsert_documents(batch_docs, batch_embeddings)
        print(f"   Batch {i//batch_size + 1}/{total_batches} done.")

    print("\n🎉 Ingestion Complete!")

if __name__ == "__main__":
    download_and_ingest()
