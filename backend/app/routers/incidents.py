
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import random
import uuid
from datetime import datetime

router = APIRouter()

# Schema matching frontend Alert interface
class IncidentFeatures(BaseModel):
    alert_burst_count: int
    hour_of_day: int
    day_of_week: int
    Category: str
    all_features: Optional[Dict[str, Any]] = None

class Incident(BaseModel):
    id: str
    title: str
    severity: str
    category: str
    source: str
    timestamp: str
    classification: str
    confidence: float
    description: str
    features: IncidentFeatures

# Initial Mock Data (Store in memory)
INCIDENTS_STORE: List[Incident] = [
    Incident(
        id="INC-2024-001",
        title="Suspicious PowerShell Execution",
        severity="critical",
        category="Execution",
        source="Azure Sentinel",
        timestamp="10 mins ago",
        classification="TP",
        confidence=96.0,
        description="Detected encoded PowerShell command execution on production database server.",
        features=IncidentFeatures(
            alert_burst_count=50,
            hour_of_day=2,
            day_of_week=5,
            Category="Execution",
            all_features={
                "alert_burst_count": 50,
                "hour_of_day": 2,
                "Category": "Execution",
                "IpAddress": "192.168.1.100",
                "Severity": "High",
                "ActionGrouped": "Execution"
            }
        )
    ),
    Incident(
        id="INC-2024-002",
        title="Impossible Travel Detection",
        severity="high",
        category="Initial Access",
        source="Azure AD",
        timestamp="25 mins ago",
        classification="TP",
        confidence=88.0,
        description="User logged in from New York and Tokyo within 1 hour.",
        features=IncidentFeatures(
            alert_burst_count=2,
            hour_of_day=14,
            day_of_week=1,
            Category="Initial Access",
            all_features={
                "alert_burst_count": 2,
                "hour_of_day": 14,
                "Category": "Initial Access",
                "IpAddress": "203.0.113.5",
                "Severity": "Medium"
            }
        )
    )
]

@router.get("/", response_model=List[Incident])
def get_incidents():
    """Fetch all active incidents."""
    # Return reversed so newest are first (if we append new ones to end)
    return list(reversed(INCIDENTS_STORE))

@router.post("/create", response_model=Incident)
def create_incident(incident: Incident):
    """Create a new incident (Internal/Simulator use)."""
    # Auto-generate timestamp if just "now"
    if incident.timestamp == "now":
        incident.timestamp = "Just now"
    
    INCIDENTS_STORE.append(incident)
    
    # Keep store size manageable
    if len(INCIDENTS_STORE) > 100:
        INCIDENTS_STORE.pop(0)
        
    return incident

@router.get("/{incident_id}", response_model=Incident)
def get_incident_detail(incident_id: str):
    for inc in INCIDENTS_STORE:
        if inc.id == incident_id:
            return inc
    raise HTTPException(status_code=404, detail="Incident not found")
