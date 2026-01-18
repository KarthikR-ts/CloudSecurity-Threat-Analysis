
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.auth import require_role
from app.rag.embeddings import generate_embedding
from app.rag.vector_db import query_vectors
from app.rag.rag_pipeline import generate_remediation_advice, format_search_results_for_rag

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 3
    filters: Optional[Dict[str, Any]] = None

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]

class AskRequest(BaseModel):
    query: str
    top_k: int = 5

class AskResponse(BaseModel):
    query: str
    advice: str
    sources: List[Dict[str, Any]]

@router.post("/search", response_model=SearchResponse)
async def search_knowledge_base(request: SearchRequest):
    try:
        # 1. Generate Embedding
        embedding = generate_embedding(request.query)
        
        # 2. Search Vector DB
        search_results = query_vectors(vector=embedding, top_k=request.top_k)
        
        # 3. Format Response
        matches = search_results.get("matches", [])
        formatted_results = []
        
        for match in matches:
            formatted_results.append({
                "id": match.get("id"),
                "score": match.get("score"),
                "content": match.get("metadata", {}).get("text", ""),
                "source": match.get("metadata", {}).get("source", "Unknown"),
                "metadata": match.get("metadata", {})
            })
            
        return SearchResponse(results=formatted_results)

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"RAG search error: {str(e)}")


@router.post("/ask", response_model=AskResponse)
async def ask_rag(request: AskRequest):
    """
    Full RAG endpoint: Search knowledge base + Generate AI remediation advice.
    
    This combines vector search with Gemini LLM to provide grounded,
    actionable security remediation guidance.
    """
    try:
        # 1. Generate embedding for query
        embedding = generate_embedding(request.query)
        
        # 2. Search vector database
        search_results = query_vectors(vector=embedding, top_k=request.top_k)
        matches = search_results.get("matches", [])
        
        # 3. Format results for RAG pipeline
        context_docs = format_search_results_for_rag(matches)
        
        # 4. Generate AI advice using Gemini
        advice = generate_remediation_advice(request.query, context_docs)
        
        return AskResponse(
            query=request.query,
            advice=advice,
            sources=context_docs
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"RAG ask error: {str(e)}")


@router.get("/status", dependencies=[Depends(require_role("analyst"))])
def get_rag_status():
    """Get RAG system status including knowledge base stats."""
    from app.rag.vector_db import get_index
    
    index = get_index()
    kb_status = "connected" if index else "disconnected"
    
    return {
        "status": "online",
        "embedding_model": "all-MiniLM-L6-v2",
        "llm_model": "gemini-1.5-flash",
        "knowledge_base": kb_status
    }


class FixRequest(BaseModel):
    description: str
    top_k: int = 3
    platform: str = "azure_cli" # or "terraform"

class FixResponse(BaseModel):
    script: str
    platform: str

@router.post("/fix", response_model=FixResponse)
async def generate_fix(request: FixRequest):
    """
    Generate an executable remediation script (Azure CLI / Terraform).
    """
    try:
        from app.rag.rag_pipeline import generate_fix_script
        
        # 1. Retrieve context first
        embedding = generate_embedding(request.description)
        search_results = query_vectors(vector=embedding, top_k=request.top_k)
        matches = search_results.get("matches", [])
        context_docs = format_search_results_for_rag(matches)
        
        # 2. Generate Script
        script = generate_fix_script(request.description, context_docs, request.platform)
        
        return FixResponse(script=script, platform=request.platform)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Script generation error: {str(e)}")
