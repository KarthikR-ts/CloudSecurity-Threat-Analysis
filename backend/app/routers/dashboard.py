
from fastapi import APIRouter, Depends
from app.auth import require_role

router = APIRouter()

@router.get("/enterprise")
def get_enterprise_dashboard(role: str = Depends(require_role("enterprise"))):
    return {
        "message": "Welcome to the Enterprise Dashboard",
        "data": {"revenue": "10M", "active_users": 5000}
    }

@router.get("/ml")
def get_ml_dashboard(role: str = Depends(require_role("ml_researcher"))):
    return {
        "message": "Welcome to the ML Researcher Dashboard",
        "status": "Systems Operational"
    }

@router.get("/vendor")
def get_vendor_dashboard(role: str = Depends(require_role("vendor"))):
    return {
        "message": "Welcome to the Vendor Dashboard",
        "inventory": {"servers": 50, "gpus": 12}
    }
