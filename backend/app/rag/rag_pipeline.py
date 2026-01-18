"""
RAG Pipeline with Gemini API Integration.
Provides grounded remediation advice based on retrieved security documents.
"""

import os
from typing import List, Dict

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. LLM generation disabled.")


def get_gemini_client():
    """Initialize Gemini client with API key."""
    if not GEMINI_AVAILABLE:
        return None
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found in environment variables.")
        return None
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')


def generate_remediation_advice(query: str, context_docs: List[Dict]) -> str:
    """
    Generate grounded remediation advice using Gemini + retrieved context.
    
    Args:
        query: The security question or incident description
        context_docs: List of retrieved documents with 'content' and 'source' keys
    
    Returns:
        AI-generated remediation advice grounded in the retrieved documents
    """
    model = get_gemini_client()
    
    if model is None:
        # Fallback: Return formatted context without LLM synthesis
        fallback_response = "**Retrieved Security Context:**\n\n"
        for i, doc in enumerate(context_docs, 1):
            fallback_response += f"{i}. [{doc.get('source', 'Unknown')}]\n"
            fallback_response += f"   {doc.get('content', 'No content')[:300]}...\n\n"
        fallback_response += "\n*Note: LLM generation unavailable. Showing raw retrieved documents.*"
        return fallback_response
    
    # Format context from retrieved documents
    context_text = "\n\n".join([
        f"[Source: {doc.get('source', 'Unknown')}]\n{doc.get('content', '')}"
        for doc in context_docs
    ])
    
    system_prompt = """You are an expert cloud security analyst. Your role is to provide 
specific, actionable remediation advice based ONLY on the provided context documents.

Instructions:
1. Analyze the security query carefully
2. Use ONLY information from the provided context documents
3. Always cite which source your advice comes from (e.g., [MITRE ATT&CK], [Azure Policy])
4. Provide step-by-step remediation actions when applicable
5. If the context doesn't contain relevant information, clearly state that
6. Be concise but thorough

Format your response as:
## Summary
Brief overview of the issue

## Remediation Steps
1. Step 1 [Source]
2. Step 2 [Source]
...

## Additional Recommendations
Any preventive measures or best practices"""

    user_prompt = f"""Context Documents:
{context_text}

---

Security Query: {query}

Based on the above context, provide specific remediation advice."""

    try:
        response = model.generate_content(
            f"{system_prompt}\n\n{user_prompt}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=1000,
            )
        )
        return response.text
    except Exception as e:
        return f"Error generating advice: {str(e)}\n\nFalling back to retrieved context:\n{context_text[:500]}..."


def format_search_results_for_rag(matches: List[Dict]) -> List[Dict]:
    """
    Format Pinecone search results into the format expected by generate_remediation_advice.
    
    Args:
        matches: Raw matches from Pinecone query
    
    Returns:
        List of formatted documents with 'content' and 'source' keys
    """
    formatted = []
    for match in matches:
        metadata = match.get("metadata", {})
        formatted.append({
            "content": metadata.get("text", ""),
            "source": metadata.get("source", "Unknown"),
            "score": match.get("score", 0),
            "id": match.get("id", "")
        })
    return formatted


def generate_fix_script(description: str, context_docs: List[Dict], platform: str = "azure_cli") -> str:
    """
    Generate an automated remediation script (Azure CLI or Terraform).
    """
    model = get_gemini_client()
    if model is None:
        return "# Error: Gemini LLM not configured."
    
    context_text = "\n\n".join([
        f"[Source: {doc.get('source', 'Unknown')}]\n{doc.get('content', '')}"
        for doc in context_docs
    ])
    
    system_prompt = f"""You are a DevOps Security Engineer expert in {platform}.
Your goal is to write a PRODUCTION-READY remediation script to fix a cloud security vulnerability.

Rules:
1. Output ONLY the code block (no markdown backticks, no explanatory text around it).
2. Include comments explaining what each command does.
3. Use variables for resource names (e.g., RESOURCE_GROUP="my-rg") so it's reusable.
4. If the fix requires multiple steps, script them broadly.
5. Base the logic on the provided security context policies."""

    user_prompt = f"""Context Policies:
{context_text}

---

Vulnerability Description: {description}

Task: Write a {platform} script to remediate this vulnerability."""

    try:
        response = model.generate_content(
            f"{system_prompt}\n\n{user_prompt}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.2, # Low temp for code
                max_output_tokens=1000,
            )
        )
        return response.text.replace("```bash", "").replace("```hcl", "").replace("```", "").strip()
    except Exception as e:
        return f"# Error generating script: {str(e)}"
