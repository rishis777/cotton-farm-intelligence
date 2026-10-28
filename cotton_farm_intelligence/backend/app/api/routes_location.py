"""
Location and Geocoding API Routes.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any, List
from app.services.geocoding_service import validate_coordinates, search_location_nominatim, TALUKAS
from app.schemas.schemas import LocationValidationResponse

router = APIRouter(prefix="/api/location", tags=["Location & Geocoding"])

@router.get("/validate", response_model=LocationValidationResponse)
def validate_location(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude between -90 and 90"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude between -180 and 180")
):
    """Validates coordinates and detects Dhule District and Taluka administrative context."""
    res = validate_coordinates(lat, lon)
    return LocationValidationResponse(**res)

@router.get("/search")
async def search_location(q: str = Query(..., min_length=2, description="Location search query (e.g. 'Dhule', 'Shirpur')")):
    """Searches geographic locations using OpenStreetMap Nominatim with local fallback."""
    results = await search_location_nominatim(q)
    return {"query": q, "results": results}

@router.get("/talukas")
def get_dhule_talukas():
    """Returns official Talukas of Dhule District with representative coordinates for quick map navigation."""
    return [
        {"name": name, "latitude": data["lat"], "longitude": data["lon"], "description": data["desc"]}
        for name, data in TALUKAS.items()
    ]
