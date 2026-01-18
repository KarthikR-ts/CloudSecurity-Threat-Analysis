
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from app.routers import auth, dashboard, ml

app = FastAPI(title="Cloud Sentinel API")

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    # Add production URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
from app.routers import incidents
app.include_router(incidents.router, prefix="/api/incidents", tags=["Incidents"])
app.include_router(ml.router, prefix="/api/ml", tags=["ML"])
from app.routers import predict
app.include_router(predict.router, prefix="/api/predict", tags=["Prediction"])
from app.routers import rag
app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])

@app.get("/")
def read_root():
    return {"status": "ok", "service": "Cloud Sentinel Backend"}
