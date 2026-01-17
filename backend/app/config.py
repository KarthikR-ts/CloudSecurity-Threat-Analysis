
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    # If we need the JWT secret for local verification without API call (optional but faster)
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")

settings = Settings()
