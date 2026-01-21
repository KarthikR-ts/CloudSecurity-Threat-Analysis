"""
Role-Aware RAG Guidance Router
Provides persona-specific remediation guidance using RAG pipeline
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum

router = APIRouter()

class UserRole(str, Enum):
    CLOUD_ENGINEER = "CLOUD_ENGINEER"
    NON_TECHNICAL = "NON_TECHNICAL"
    ML_ENGINEER = "ML_ENGINEER"

class GuidanceResponse(BaseModel):
    alert_id: str
    role: UserRole
    guidance: str
    remediation_steps: List[str]
    code_snippets: Optional[List[Dict[str, str]]] = None
    business_context: Optional[str] = None
    technical_analysis: Optional[str] = None
    sources: List[Dict[str, Any]] = []

# Role-specific prompt templates
ROLE_PROMPTS = {
    UserRole.CLOUD_ENGINEER: """
You are a senior cloud security engineer. Provide concrete Azure remediation steps.
Include:
- Specific Azure CLI or PowerShell commands
- NSG rule modifications if applicable
- RBAC/IAM changes needed
- Encryption and network security recommendations
- Azure Policy remediation tasks

Be technical and actionable. Reference specific Azure services and configurations.
""",
    
    UserRole.NON_TECHNICAL: """
You are explaining a security issue to a business executive with no technical background.
Provide:
- Plain language explanation of what happened
- Business impact (financial, regulatory, reputational)
- What happens if this is ignored
- What to tell your IT team to fix (in simple terms)
- Estimated urgency and timeline

Avoid technical jargon. Focus on business risk and outcomes.
""",
    
    UserRole.ML_ENGINEER: """
You are a machine learning engineer analyzing model predictions.
Provide:
- Technical analysis linking feature values to SHAP contributions
- Connection between features and MITRE ATT&CK tactics
- Mapping to CIS Azure Benchmark controls
- Model confidence interpretation
- Potential false positive indicators

Focus on explainability and model behavior analysis.
"""
}

# Demo guidance responses (for when RAG is not available)
DEMO_GUIDANCE = {
    "ALT-2024-DEMO01": {
        UserRole.CLOUD_ENGINEER: GuidanceResponse(
            alert_id="ALT-2024-DEMO01",
            role=UserRole.CLOUD_ENGINEER,
            guidance="Public blob access on storage account 'prodfinancedata' must be disabled immediately to prevent data exposure.",
            remediation_steps=[
                "1. Disable anonymous blob access at storage account level",
                "2. Review and revoke any SAS tokens with public access",
                "3. Enable private endpoints for secure connectivity",
                "4. Configure network rules to allow only trusted VNets",
                "5. Enable storage analytics logging for audit trail"
            ],
            code_snippets=[
                {
                    "title": "Disable Public Blob Access (Azure CLI)",
                    "language": "bash",
                    "code": """# Disable public blob access
az storage account update \\
    --name prodfinancedata \\
    --resource-group rg-production \\
    --allow-blob-public-access false

# Configure network rules
az storage account network-rule add \\
    --account-name prodfinancedata \\
    --resource-group rg-production \\
    --vnet-name production-vnet \\
    --subnet app-subnet"""
                },
                {
                    "title": "Enable Private Endpoint (PowerShell)",
                    "language": "powershell",
                    "code": """# Create private endpoint
$storage = Get-AzStorageAccount -ResourceGroupName "rg-production" -Name "prodfinancedata"
$privateEndpoint = New-AzPrivateEndpoint `
    -Name "pe-prodfinancedata" `
    -ResourceGroupName "rg-production" `
    -Location "eastus" `
    -Subnet $subnet `
    -PrivateLinkServiceConnection $connection"""
                }
            ],
            sources=[
                {"title": "CIS Azure 3.11", "type": "benchmark"},
                {"title": "T1530 - Data from Cloud Storage", "type": "mitre"}
            ]
        ),
        UserRole.NON_TECHNICAL: GuidanceResponse(
            alert_id="ALT-2024-DEMO01",
            role=UserRole.NON_TECHNICAL,
            guidance="A storage location containing customer financial data is currently accessible to anyone on the internet. This is similar to leaving a filing cabinet unlocked on a public sidewalk.",
            remediation_steps=[
                "1. URGENT: Contact IT immediately to restrict access",
                "2. Legal team should assess GDPR notification requirements",
                "3. Audit what data may have been accessed",
                "4. Prepare incident response communication",
                "5. Schedule security review of all cloud storage"
            ],
            business_context="""
**What's at Risk:**
- Customer financial records (account numbers, transactions)
- Potential GDPR fine: Up to €20M or 4% of annual revenue
- Reputational damage if breach becomes public
- Customer trust erosion

**If Ignored:**
- Data may already be indexed by search engines
- Attackers actively scan for exposed storage
- Regulatory investigation if breach is reported

**Timeline:** Fix within 4 hours. This is a CRITICAL issue.
""",
            sources=[
                {"title": "GDPR Article 33 - Breach Notification", "type": "regulation"}
            ]
        ),
        UserRole.ML_ENGINEER: GuidanceResponse(
            alert_id="ALT-2024-DEMO01",
            role=UserRole.ML_ENGINEER,
            guidance="Model predicted TRUE_POSITIVE with 93% confidence. SHAP analysis shows 'public_access_enabled' as the primary driver.",
            remediation_steps=[
                "1. Review feature contribution waterfall",
                "2. Validate prediction against ground truth if available",
                "3. Check for similar patterns in training data",
                "4. Monitor for drift in public_access feature distribution"
            ],
            technical_analysis="""
**SHAP Value Analysis:**

| Feature | Value | SHAP Contribution |
|---------|-------|-------------------|
| public_access_enabled | 1 | +0.42 (strongest positive) |
| contains_sensitive_data | 1 | +0.28 |
| encryption_at_rest | 0 | -0.15 (would reduce risk) |
| network_rules_count | 0 | -0.12 |

**MITRE ATT&CK Mapping:**
- T1530 (Data from Cloud Storage): Direct match - exposed storage is primary vector

**Model Confidence Breakdown:**
- Base rate: 0.33 (uniform prior)
- After features: 0.93 (TRUE_POSITIVE)
- Margin to decision boundary: 0.43 (high confidence)

**False Positive Indicators:** None detected. Strong signal from multiple correlated features.
""",
            sources=[
                {"title": "XGBoost Model v2.1", "type": "model"},
                {"title": "SHAP TreeExplainer", "type": "explainer"}
            ]
        )
    }
}

@router.get("/{alert_id}/guidance", response_model=GuidanceResponse)
async def get_role_guidance(
    alert_id: str,
    role: UserRole = Query(UserRole.CLOUD_ENGINEER, description="User role for guidance customization")
):
    """
    Get role-specific remediation guidance for an alert.
    Uses RAG pipeline with persona-aware prompting.
    """
    
    # Check for demo guidance first
    if alert_id in DEMO_GUIDANCE and role in DEMO_GUIDANCE[alert_id]:
        return DEMO_GUIDANCE[alert_id][role]
    
    # For non-demo alerts, try to use RAG pipeline
    try:
        from app.rag.embeddings import generate_embedding
        from app.rag.vector_db import query_vectors
        from app.rag.rag_pipeline import format_search_results_for_rag
        import google.generativeai as genai
        import os
        
        # Get alert details (simplified for demo)
        alert_title = f"Security Alert {alert_id}"
        
        # Generate embedding and search
        query = f"How to remediate {alert_title}"
        embedding = generate_embedding(query)
        search_results = query_vectors(vector=embedding, top_k=5)
        matches = search_results.get("matches", [])
        context_docs = format_search_results_for_rag(matches)
        
        # Build role-specific prompt
        role_prompt = ROLE_PROMPTS.get(role, ROLE_PROMPTS[UserRole.CLOUD_ENGINEER])
        
        context_text = "\n".join([
            f"Source: {doc.get('source', 'Unknown')}\nContent: {doc.get('text', '')}"
            for doc in context_docs
        ])
        
        full_prompt = f"""
{role_prompt}

Alert: {alert_title}

Relevant security knowledge:
{context_text}

Provide guidance appropriate for your role.
"""
        
        # Generate with Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-3-flash-preview")
        response = model.generate_content(full_prompt)
        
        return GuidanceResponse(
            alert_id=alert_id,
            role=role,
            guidance=response.text,
            remediation_steps=["See guidance above for detailed steps"],
            sources=[{"title": doc.get("source", "Unknown"), "type": "rag"} for doc in context_docs[:3]]
        )
        
    except Exception as e:
        # Fallback response
        return GuidanceResponse(
            alert_id=alert_id,
            role=role,
            guidance=f"Unable to generate personalized guidance. Error: {str(e)}",
            remediation_steps=[
                "1. Review alert details manually",
                "2. Consult security documentation",
                "3. Contact SOC team for assistance"
            ],
            sources=[]
        )

@router.get("/templates")
async def get_prompt_templates():
    """Return the prompt templates used for each role (for transparency)."""
    return {
        role.value: prompt.strip()
        for role, prompt in ROLE_PROMPTS.items()
    }
