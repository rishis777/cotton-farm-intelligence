"""
Environment and Soil API Routes.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any
from app.services.weather_service import fetch_weather_data
from app.services.soil_service import fetch_soil_data
from app.schemas.schemas import EnvironmentDataResponse, SoilDataResponse

router = APIRouter(prefix="/api", tags=["Environment & Soil"])

@router.get("/environment", response_model=EnvironmentDataResponse)
async def get_environment_data(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0)
):
    """Retrieves live current weather, 7-day forecast, and cotton seasonal metrics from Open-Meteo."""
    data = await fetch_weather_data(lat, lon)
    return EnvironmentDataResponse(**data)

@router.get("/soil", response_model=SoilDataResponse)
async def get_soil_data(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0)
):
    """Retrieves soil properties (pH, Clay %, Sand %, Silt %, SOC) via ISRIC SoilGrids 2.0 or ICAR baseline."""
    data = await fetch_soil_data(lat, lon)
    return SoilDataResponse(**data)
