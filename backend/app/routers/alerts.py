"""
Enhanced Alerts Router with Priority Scoring and SSE Streaming
Aurora CSPM Platform
"""

import asyncio
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from enum import Enum
import uuid

router = APIRouter()

# ============================================================================
# ENUMS & MODELS
# ============================================================================

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PredictionClass(str, Enum):
    TRUE_POSITIVE = "TRUE_POSITIVE"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    BENIGN_POSITIVE = "BENIGN_POSITIVE"

class UserRole(str, Enum):
    CLOUD_ENGINEER = "CLOUD_ENGINEER"
    NON_TECHNICAL = "NON_TECHNICAL"
    ML_ENGINEER = "ML_ENGINEER"

class ResourceType(str, Enum):
    VM = "VM"
    STORAGE_ACCOUNT = "StorageAccount"
    SQL_DB = "SQLDB"
    AKS_CLUSTER = "AKSCluster"
    KEY_VAULT = "KeyVault"
    NSG = "NetworkSecurityGroup"
    IDENTITY = "Identity"
    FUNCTION_APP = "FunctionApp"


class EnhancedAlert(BaseModel):
    id: str = Field(default_factory=lambda: f"ALT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}")
    title: str
    description: str
    resource_type: ResourceType
    resource_name: str
    severity: AlertSeverity
    xgb_prediction: PredictionClass
    xgb_confidence: float = Field(ge=0, le=1)
    priority_score: float = Field(ge=0, le=100)
    mitre_techniques: List[str] = []
    cis_controls: List[str] = []
    azure_policies: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Business context for non-technical users
    business_impact: Optional[str] = None
    risk_category: str = "Security"  # Data, Identity, Network, Compute
    
    # ML context
    features: Dict[str, Any] = {}
    shap_values: Optional[Dict[str, float]] = None

class AlertsResponse(BaseModel):
    alerts: List[EnhancedAlert]
    total: int
    page: int
    page_size: int
    workload_stats: Dict[str, Any]

# ============================================================================
# IN-MEMORY ALERT STORE (for demo)
# ============================================================================

_alerts_store: List[EnhancedAlert] = []
_connected_clients = []

def calculate_priority_score(severity: AlertSeverity, confidence: float) -> float:
    """Calculate priority score based on severity and ML confidence."""
    severity_weights = {
        AlertSeverity.LOW: 25,
        AlertSeverity.MEDIUM: 50,
        AlertSeverity.HIGH: 75,
        AlertSeverity.CRITICAL: 100
    }
    base_score = severity_weights.get(severity, 50)
    return round(base_score * confidence, 1)

def seed_demo_alerts():
    """Seed initial demo alerts for the dashboard."""
    global _alerts_store
    
    demo_alerts = [
        EnhancedAlert(
            id="ALT-2024-DEMO01",
            title="Public Azure Storage Account with Read Access",
            description="Storage account 'prodfinancedata' has anonymous blob read access enabled, potentially exposing sensitive financial records.",
            resource_type=ResourceType.STORAGE_ACCOUNT,
            resource_name="prodfinancedata",
            severity=AlertSeverity.CRITICAL,
            xgb_prediction=PredictionClass.TRUE_POSITIVE,
            xgb_confidence=0.93,
            priority_score=93.0,
            mitre_techniques=["T1530 - Data from Cloud Storage"],
            cis_controls=["CIS Azure 3.11 - Secure transfer required", "CIS Azure 3.7 - Public access disabled"],
            azure_policies=["Audit public blob access", "Storage accounts should restrict network access"],
            business_impact="Customer financial data exposed. Potential GDPR fine of €20M or 4% annual revenue.",
            risk_category="Data",
            features={
                "public_access_enabled": 1,
                "contains_sensitive_data": 1,
                "encryption_at_rest": 0,
                "network_rules_count": 0,
                "last_access_days": 2
            },
            shap_values={
                "public_access_enabled": 0.42,
                "contains_sensitive_data": 0.28,
                "encryption_at_rest": -0.15,
                "network_rules_count": -0.12,
                "last_access_days": 0.08
            }
        ),
        EnhancedAlert(
            id="ALT-2024-DEMO02",
            title="Suspicious PowerShell Execution on Production VM",
            description="Encoded PowerShell command detected on VM 'prod-db-01' executing during non-business hours.",
            resource_type=ResourceType.VM,
            resource_name="prod-db-01",
            severity=AlertSeverity.HIGH,
            xgb_prediction=PredictionClass.TRUE_POSITIVE,
            xgb_confidence=0.87,
            priority_score=65.25,
            mitre_techniques=["T1059.001 - PowerShell", "T1027 - Obfuscated Files"],
            cis_controls=["CIS Azure 7.1 - Enable Azure Defender"],
            azure_policies=["Adaptive application controls should be enabled"],
            business_impact="Potential ransomware deployment. Could result in 72-hour business disruption.",
            risk_category="Compute",
            features={
                "encoded_command": 1,
                "execution_hour": 3,
                "is_production": 1,
                "user_is_admin": 1,
                "command_length": 2048
            },
            shap_values={
                "encoded_command": 0.35,
                "execution_hour": 0.22,
                "is_production": 0.18,
                "user_is_admin": 0.12,
                "command_length": 0.08
            }
        ),
        EnhancedAlert(
            id="ALT-2024-DEMO03",
            title="SQL Database Firewall Rule Allows Any IP",
            description="Azure SQL Database 'customerdb' has firewall rule 0.0.0.0-255.255.255.255 allowing connections from any IP.",
            resource_type=ResourceType.SQL_DB,
            resource_name="customerdb",
            severity=AlertSeverity.CRITICAL,
            xgb_prediction=PredictionClass.TRUE_POSITIVE,
            xgb_confidence=0.91,
            priority_score=91.0,
            mitre_techniques=["T1190 - Exploit Public-Facing Application"],
            cis_controls=["CIS Azure 4.1.1 - Auditing enabled on SQL servers"],
            azure_policies=["SQL servers should use private endpoints"],
            business_impact="Customer PII database accessible from internet. Compliance violation risk.",
            risk_category="Data",
            features={
                "firewall_any_ip": 1,
                "contains_pii": 1,
                "private_endpoint": 0,
                "tls_version": 1.0
            },
            shap_values={
                "firewall_any_ip": 0.45,
                "contains_pii": 0.25,
                "private_endpoint": -0.18,
                "tls_version": 0.10
            }
        ),
        EnhancedAlert(
            id="ALT-2024-DEMO04",
            title="AKS Cluster Running Privileged Containers",
            description="Kubernetes pods in 'prod-microservices' namespace running with privileged security context.",
            resource_type=ResourceType.AKS_CLUSTER,
            resource_name="prod-aks-01",
            severity=AlertSeverity.MEDIUM,
            xgb_prediction=PredictionClass.BENIGN_POSITIVE,
            xgb_confidence=0.72,
            priority_score=36.0,
            mitre_techniques=["T1611 - Escape to Host"],
            cis_controls=["CIS Azure 8.5 - Pod security policies"],
            azure_policies=["Azure Kubernetes clusters should not grant CAP_SYS_ADMIN"],
            business_impact="Known DevOps requirement for monitoring agents. Low risk if contained.",
            risk_category="Compute",
            features={
                "privileged_container": 1,
                "namespace": "monitoring",
                "image_verified": 1,
                "network_policy": 1
            },
            shap_values={
                "privileged_container": 0.15,
                "namespace": -0.25,
                "image_verified": -0.18,
                "network_policy": -0.12
            }
        ),
        EnhancedAlert(
            id="ALT-2024-DEMO05",
            title="Key Vault Access from Unknown IP",
            description="Azure Key Vault 'prod-secrets' accessed from IP not in allowlist.",
            resource_type=ResourceType.KEY_VAULT,
            resource_name="prod-secrets",
            severity=AlertSeverity.HIGH,
            xgb_prediction=PredictionClass.FALSE_POSITIVE,
            xgb_confidence=0.68,
            priority_score=51.0,
            mitre_techniques=["T1552.001 - Credentials In Files"],
            cis_controls=["CIS Azure 8.1 - Key Vault logging enabled"],
            azure_policies=["Key Vault should use private endpoint"],
            business_impact="Legitimate DevOps pipeline from new Azure region. Verify with IT.",
            risk_category="Identity",
            features={
                "ip_in_allowlist": 0,
                "user_service_principal": 1,
                "operation_type": "get_secret",
                "time_of_day": 14
            },
            shap_values={
                "ip_in_allowlist": 0.22,
                "user_service_principal": -0.35,
                "operation_type": -0.08,
                "time_of_day": -0.12
            }
        )
    ]
    
    _alerts_store = demo_alerts

# Seed on module load
seed_demo_alerts()

# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/", response_model=AlertsResponse)
async def get_alerts(
    role: Optional[UserRole] = Query(None, description="User role for view customization"),
    severity: Optional[AlertSeverity] = Query(None),
    prediction: Optional[PredictionClass] = Query(None),
    sort_by: str = Query("priority_score", description="Sort field"),
    sort_order: str = Query("desc", description="asc or desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    Get alerts with role-based filtering and priority sorting.
    """
    alerts = _alerts_store.copy()
    
    # Filter by severity
    if severity:
        alerts = [a for a in alerts if a.severity == severity]
    
    # Filter by prediction class
    if prediction:
        alerts = [a for a in alerts if a.xgb_prediction == prediction]
    
    # Sort
    reverse = sort_order == "desc"
    if sort_by == "priority_score":
        alerts.sort(key=lambda x: x.priority_score, reverse=reverse)
    elif sort_by == "timestamp":
        alerts.sort(key=lambda x: x.timestamp, reverse=reverse)
    elif sort_by == "confidence":
        alerts.sort(key=lambda x: x.xgb_confidence, reverse=reverse)
    
    # Pagination
    total = len(alerts)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = alerts[start:end]
    
    # Calculate workload stats
    total_alerts = len(_alerts_store)
    auto_classified = len([a for a in _alerts_store if a.xgb_confidence >= 0.7])
    manual_review = total_alerts - auto_classified
    
    workload_stats = {
        "total_alerts": total_alerts,
        "auto_classified": auto_classified,
        "manual_review_needed": manual_review,
        "workload_reduction_pct": round((auto_classified / max(total_alerts, 1)) * 100, 1),
        "true_positives": len([a for a in _alerts_store if a.xgb_prediction == PredictionClass.TRUE_POSITIVE]),
        "false_positives": len([a for a in _alerts_store if a.xgb_prediction == PredictionClass.FALSE_POSITIVE]),
        "benign_positives": len([a for a in _alerts_store if a.xgb_prediction == PredictionClass.BENIGN_POSITIVE])
    }
    
    return AlertsResponse(
        alerts=paginated,
        total=total,
        page=page,
        page_size=page_size,
        workload_stats=workload_stats
    )

@router.get("/{alert_id}")
async def get_alert(alert_id: str):
    """Get single alert by ID."""
    for alert in _alerts_store:
        if alert.id == alert_id:
            return alert
    raise HTTPException(status_code=404, detail="Alert not found")

@router.get("/stream/live")
async def stream_alerts():
    """
    SSE endpoint for real-time alert streaming.
    Clients connect here to receive live updates.
    """
    async def event_generator():
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connected', 'message': 'SSE stream established'})}\n\n"
        
        last_count = len(_alerts_store)
        
        while True:
            await asyncio.sleep(3)  # Check every 3 seconds
            
            current_count = len(_alerts_store)
            
            # Send current stats
            stats = {
                "type": "stats",
                "total_alerts": current_count,
                "new_alerts": current_count - last_count if current_count > last_count else 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            yield f"data: {json.dumps(stats)}\n\n"
            
            # If new alerts, send them
            if current_count > last_count:
                new_alerts = _alerts_store[last_count:]
                for alert in new_alerts:
                    alert_data = {
                        "type": "new_alert",
                        "alert": alert.model_dump(mode='json')
                    }
                    yield f"data: {json.dumps(alert_data, default=str)}\n\n"
            
            last_count = current_count
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.post("/simulate")
async def simulate_alert(alert_data: Optional[Dict[str, Any]] = None):
    """
    Add a simulated alert to the store (for demo purposes).
    """
    import random
    
    if alert_data:
        new_alert = EnhancedAlert(**alert_data)
    else:
        # Generate random alert
        severities = [AlertSeverity.LOW, AlertSeverity.MEDIUM, AlertSeverity.HIGH, AlertSeverity.CRITICAL]
        predictions = [PredictionClass.TRUE_POSITIVE, PredictionClass.FALSE_POSITIVE, PredictionClass.BENIGN_POSITIVE]
        
        severity = random.choice(severities)
        confidence = round(random.uniform(0.5, 0.99), 2)
        
        new_alert = EnhancedAlert(
            title=f"Simulated Security Alert {len(_alerts_store) + 1}",
            description="Auto-generated alert for demonstration purposes.",
            resource_type=random.choice(list(ResourceType)),
            resource_name=f"demo-resource-{random.randint(100, 999)}",
            severity=severity,
            xgb_prediction=random.choice(predictions),
            xgb_confidence=confidence,
            priority_score=calculate_priority_score(severity, confidence),
            mitre_techniques=["T1078 - Valid Accounts"],
            cis_controls=["CIS Azure 1.1"],
            azure_policies=["Demo Policy"],
            risk_category=random.choice(["Data", "Identity", "Network", "Compute"])
        )
    
    _alerts_store.insert(0, new_alert)
    return {"status": "created", "alert_id": new_alert.id}

@router.get("/metrics/summary")
async def get_metrics_summary():
    """Get summary metrics for dashboard cards."""
    total = len(_alerts_store)
    
    severity_counts = {
        "critical": len([a for a in _alerts_store if a.severity == AlertSeverity.CRITICAL]),
        "high": len([a for a in _alerts_store if a.severity == AlertSeverity.HIGH]),
        "medium": len([a for a in _alerts_store if a.severity == AlertSeverity.MEDIUM]),
        "low": len([a for a in _alerts_store if a.severity == AlertSeverity.LOW])
    }
    
    prediction_counts = {
        "true_positive": len([a for a in _alerts_store if a.xgb_prediction == PredictionClass.TRUE_POSITIVE]),
        "false_positive": len([a for a in _alerts_store if a.xgb_prediction == PredictionClass.FALSE_POSITIVE]),
        "benign_positive": len([a for a in _alerts_store if a.xgb_prediction == PredictionClass.BENIGN_POSITIVE])
    }
    
    risk_categories = {}
    for alert in _alerts_store:
        cat = alert.risk_category
        risk_categories[cat] = risk_categories.get(cat, 0) + 1
    
    # Calculate overall risk score (0-100)
    risk_score = min(100, round(
        (severity_counts["critical"] * 25 + 
         severity_counts["high"] * 15 + 
         severity_counts["medium"] * 5 + 
         prediction_counts["true_positive"] * 10) / max(total, 1) * 10
    ))
    
    return {
        "total_alerts": total,
        "severity_distribution": severity_counts,
        "prediction_distribution": prediction_counts,
        "risk_categories": risk_categories,
        "overall_risk_score": risk_score,
        "model_metrics": {
            "f1_score": 0.84,
            "precision": 0.82,
            "recall": 0.86,
            "accuracy": 0.83
        }
    }
