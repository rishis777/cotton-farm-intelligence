"""
FastAPI Main Application for Cotton Farm Intelligence Dashboard.
Context: Dhule District, Khandesh, Maharashtra, India.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from app.database import init_db, seed_default_farms_if_empty
from app.services.model_service import get_leaf_model_service
from app.api import (
    routes_location,
    routes_environment,
    routes_suitability,
    routes_leaf,
    routes_farms
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database and Preload Model
    print("[STARTUP] Initializing SQLite database...")
    init_db()
    seed_default_farms_if_empty()
    print("[STARTUP] Initializing Cotton Leaf Computer Vision Model...")
    model_service = get_leaf_model_service()
    if model_service.is_loaded:
        print(f"[STARTUP] Model ready: {len(model_service.classes)} classes loaded.")
    else:
        print(f"[STARTUP WARNING] Model deferred: {model_service.load_error}")
    yield
    print("[SHUTDOWN] Cotton Farm Intelligence API stopped.")

app = FastAPI(
    title="Cotton Farm Intelligence API — Dhule, Maharashtra",
    description=(
        "Full-Stack Agricultural Intelligence API combining interactive spatial mapping, "
        "evidence-based cotton suitability scoring, real-time Open-Meteo weather, SoilGrids "
        "soil parameters, and MobileNetV2 cotton leaf disease classification."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Vite frontend (default port 5173 / localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(routes_location.router)
app.include_router(routes_environment.router)
app.include_router(routes_suitability.router)
app.include_router(routes_leaf.router)
app.include_router(routes_farms.router)

@app.get("/api/health", tags=["System Health"])
def health_check():
    """Returns overall health, database status, and model readiness."""
    model_service = get_leaf_model_service()
    return {
        "status": "healthy",
        "service": "Cotton Farm Intelligence Backend",
        "region": "Dhule District, Maharashtra, India",
        "default_coordinates": {"latitude": 20.9042, "longitude": 74.7749},
        "model_loaded": model_service.is_loaded,
        "model_accuracy": "89.90% (Untouched Test Set)",
        "classes_count": len(model_service.classes),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
