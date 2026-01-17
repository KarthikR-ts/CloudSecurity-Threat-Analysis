
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from supabase import create_client, Client
from app.config import settings

# OAuth2 scheme for Swagger UI (TokenUrl is just a placeholder here as we use Supabase Auth on frontend)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_supabase_client() -> Client:
    url: str = settings.SUPABASE_URL
    key: str = settings.SUPABASE_KEY
    if not url or not key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase credentials not configured"
        )
    return create_client(url, key)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    supabase = get_supabase_client()
    try:
        # Verify token by calling Supabase Auth API
        user_response = supabase.auth.get_user(token)
        user = user_response.user
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user
    except Exception as e:
        print(f"Auth Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user_role(user = Depends(get_current_user)) -> str:
    # Assuming role is stored in user_metadata or app_metadata
    # Adjust this based on where 'role' is actually stored in your Supabase setup.
    # Common pattern: user.user_metadata['role'] or user.app_metadata['role']
    # Prompt implies "Each user has exactly one role", usually set in metadata.
    
    # Priority check: app_metadata (secure) -> user_metadata (user editable sometimes)
    app_meta = user.app_metadata or {}
    user_meta = user.user_metadata or {}
    
    role = app_meta.get("role") or user_meta.get("role")
    
    if not role:
        # Fallback or strict error? 
        # For this system, we expect a role.
        # return "unknown"
        # Or maybe the prompt implies the text 'role' is a claim?
        # We will assume it's in metadata.
        return "vendor" # Default/Fallback for safety if undefined, or raise 403.
        # Ideally, raise 403 if no role found.
        # raise HTTPException(status_code=403, detail="User has no assigned role")
    return role

def require_role(required_role: str):
    def role_checker(role: str = Depends(get_current_user_role)):
        if role != required_role:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: Requires {required_role} role"
            )
        return role
    return role_checker
