
from fastapi import APIRouter, Depends
from app.auth import get_current_user

router = APIRouter()

@router.post("/session")
def get_session(user = Depends(get_current_user)):
    """
    Returns the currently authenticated user and their metadata.
    """
    return {
        "id": user.id,
        "email": user.email,
        "role": user.user_metadata.get("role", "unknown"),
        "created_at": user.created_at
    }
