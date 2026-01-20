
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import random
import asyncio
from datetime import datetime
import uuid

# Import existing logic
from app.routers.predict import predict_incident, PredictionRequest
from app.routers.rag import ask_rag, AskRequest
from app.routers.alerts import EnhancedAlert, ResourceType, AlertSeverity, PredictionClass, calculate_priority_score, _alerts_store

router = APIRouter()

class SimulationStep(BaseModel):
    id: str
    name: str
    description: str
    status: str
    timestamp: str
    data: Optional[Dict[str, Any]] = None

class FullSimulationResponse(BaseModel):
    simulation_id: str
    steps: List[SimulationStep]
    result: Optional[EnhancedAlert] = None
    remediation: Optional[Dict[str, Any]] = None

@router.post("/run", response_model=FullSimulationResponse)
async def run_full_simulation():
    """
    Runs a full end-to-end simulation:
    1. Generate Synthetic Input
    2. ML Classification (Inference)
    3. RAG Remediation (Knowledge Retrieval)
    4. Store & Notify
    """
    sim_id = f"SIM-{uuid.uuid4().hex[:6].upper()}"
    steps = []

    def add_step(name: str, description: str, data: Optional[Dict[str, Any]] = None):
        steps.append(SimulationStep(
            id=str(len(steps) + 1),
            name=name,
            description=description,
            status="completed",
            timestamp=datetime.now().isoformat(),
            data=data
        ))

    # --- STEP 1: Synthetic Value Generation ---
    synthetic_scenarios = [
        {
            "title": "Unusual Data Egress detected from Storage Account",
            "resource_type": ResourceType.STORAGE_ACCOUNT,
            "resource_name": "data-lake-prod",
            "features": {
                "egress_volume_gb": 45.2,
                "destination_region": "unknown-east",
                "auth_method": "access_key",
                "is_business_hours": False,
                "alert_burst_count": 12
            }
        },
        {
            "title": "Brute Force Attempt on SQL Database",
            "resource_type": ResourceType.SQL_DB,
            "resource_name": "user-auth-db",
            "features": {
                "failed_login_count": 156,
                "source_ip_reputation": "low",
                "target_port": 1433,
                "protocol": "TDS",
                "alert_burst_count": 25
            }
        },
        {
            "title": "Privileged Role Assignment to Service Principal",
            "resource_type": ResourceType.IDENTITY,
            "resource_name": "sp-github-actions",
            "features": {
                "role_name": "Owner",
                "assigner_user": "dev-user-01",
                "is_mfa_used": False,
                "location_drift": True,
                "alert_burst_count": 3
            }
        }
    ]
    
    scenario = random.choice(synthetic_scenarios)
    add_step(
        "Data Generation", 
        f"Generated synthetic telemetry for {scenario['resource_name']}",
        {"scenario": scenario["title"], "telemetry": scenario["features"]}
    )
    
    # Simulate processing time
    await asyncio.sleep(0.5)

    # --- STEP 2: ML Model Processing ---
    try:
        pred_req = PredictionRequest(features=scenario["features"])
        # We manually call the predict logic
        ml_result = await predict_incident(pred_req)
        
        prediction_mapping = {
            "TruePositive": PredictionClass.TRUE_POSITIVE,
            "FalsePositive": PredictionClass.FALSE_POSITIVE,
            "BenignPositive": PredictionClass.BENIGN_POSITIVE,
            "Unknown": PredictionClass.TRUE_POSITIVE # Default
        }
        
        classification = prediction_mapping.get(ml_result.prediction, PredictionClass.TRUE_POSITIVE)
        
        add_step(
            "ML Classification",
            f"Model classified incident as {ml_result.prediction} with {int(ml_result.confidence * 100)}% confidence",
            {
                "prediction": ml_result.prediction,
                "confidence": ml_result.confidence,
                "probabilities": ml_result.probabilities
            }
        )
    except Exception as e:
        add_step("ML Classification", f"ML model inference failed: {str(e)}", {"status": "error"})
        classification = PredictionClass.TRUE_POSITIVE
        ml_result = None

    await asyncio.sleep(0.5)

    # --- STEP 3: RAG Remediation ---
    remediation_data = None
    
    # Predefined fallbacks for 100% demo reliability
    fallbacks = {
        "Unusual Data Egress detected from Storage Account": {
            "advice": "1. Immediately rotate Storage Account Access Keys. 2. Enable 'Secure transfer required' in storage settings. 3. Configure Virtual Network service endpoints to restrict access. 4. Review 'Storage Blob Data Reader' role assignments for unusual service principals.",
            "sources": [{"source": "Azure Security Benchmark v3"}, {"source": "MITRE ATT&CK T1530"}]
        },
        "Brute Force Attempt on SQL Database": {
            "advice": "1. Temporarily block the source IP at the NSG/Firewall level. 2. Enforce 'Microsoft Entra authentication only' for the SQL server. 3. Update SQL Firewall rules to remove 0.0.0.0/0 (Internet) access. 4. Reset passwords for any compromised local SQL accounts.",
            "sources": [{"source": "CIS Microsoft Azure v2.0"}, {"source": "SQL Security Best Practices"}]
        },
        "Privileged Role Assignment to Service Principal": {
            "advice": "1. Revoke the unauthorized 'Owner' role assignment immediately. 2. Enable 'PIM' (Privileged Identity Management) for just-in-time role activation. 3. Audit all role assignments made by user 'dev-user-01' in the last 24 hours. 4. Enforce MFA for all users with 'User Access Administrator' permissions.",
            "sources": [{"source": "Azure IAM Hardening Guide"}, {"source": "NIST 800-53"}]
        }
    }

    try:
        rag_query = f"Provide remediation for {scenario['title']} in {scenario['resource_type'].value}. Impact: {scenario['features']}."
        rag_req = AskRequest(query=rag_query, top_k=3)
        rag_resp = await ask_rag(rag_req)
        
        # Check if RAG actually returned something useful (not a failure message from LLM)
        if rag_resp.advice and "Error" not in rag_resp.advice and "relevant information" not in rag_resp.advice.lower():
            remediation_data = {
                "advice": rag_resp.advice,
                "sources": rag_resp.sources
            }
            add_step(
                "RAG Remediation",
                "Knowledge base queried for contextual fix actions",
                {"advice_preview": rag_resp.advice[:100] + "...", "source_count": len(rag_resp.sources)}
            )
        else:
            raise ValueError("RAG returned low quality or error response")
            
    except Exception as e:
        # Use high-quality fallback for reliability
        remediation_data = fallbacks.get(scenario["title"])
        add_step("RAG Remediation", f"Using cached expert-knowledge remediation (RAG pipeline bypassed/failed: {str(e)})", {"status": "fallback"})

    # --- FINAL: Create Enhanced Alert and Store ---
    severity = AlertSeverity.HIGH if classification == PredictionClass.TRUE_POSITIVE else AlertSeverity.MEDIUM
    if "failed_login" in str(scenario["features"]): severity = AlertSeverity.CRITICAL
    
    final_alert = EnhancedAlert(
        title=scenario["title"],
        description=f"Simulated alert for {scenario['resource_name']}. Details: {json.dumps(scenario['features'])}",
        resource_type=scenario["resource_type"],
        resource_name=scenario["resource_name"],
        severity=severity,
        xgb_prediction=classification,
        xgb_confidence=ml_result.confidence if ml_result else 0.85,
        priority_score=calculate_priority_score(severity, ml_result.confidence if ml_result else 0.85),
        features=scenario["features"],
        shap_values={k: random.uniform(0.05, 0.4) * (1 if random.random() > 0.3 else -1) for k in scenario["features"].keys()},
        business_impact="Simulated impact for demonstration purposes."
    )
    
    # Store it in memory so it shows up in dashboard lists
    _alerts_store.insert(0, final_alert)
    
    return FullSimulationResponse(
        simulation_id=sim_id,
        steps=steps,
        result=final_alert,
        remediation=remediation_data
    )

import json
