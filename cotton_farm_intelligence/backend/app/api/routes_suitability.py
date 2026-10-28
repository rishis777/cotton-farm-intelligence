"""
Cotton Suitability Analysis API Routes.
"""

from fastapi import APIRouter, HTTPException
import json
from app.services.suitability_engine import evaluate_cotton_suitability
from app.schemas.schemas import SuitabilityAnalysisRequest, SuitabilityAnalysisResponse
from app.database import get_db_connection

router = APIRouter(prefix="/api/suitability", tags=["Crop Suitability Analysis"])

@router.post("/analyze", response_model=SuitabilityAnalysisResponse)
async def analyze_cotton_suitability(payload: SuitabilityAnalysisRequest):
    """
    Performs evidence-based cotton suitability analysis for specified coordinates.
    Considers climate, Vertisol soil traits, moisture context, and documents all constraints.
    """
    result = await evaluate_cotton_suitability(
        lat=payload.latitude,
        lon=payload.longitude,
        irrigation_available=payload.irrigation_available or False,
        user_notes=payload.notes
    )

    # Persist in analysis history table
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO analysis_history 
                (latitude, longitude, suitability_category, suitability_score, evidence_json)
                VALUES (?, ?, ?, ?, ?)
            """, (
                payload.latitude,
                payload.longitude,
                result["category"],
                result["overall_score"],
                json.dumps(result)
            ))
            conn.commit()
    except Exception as e:
        print(f"[HISTORY LOGGING NOTICE] Could not save history: {e}")

    return SuitabilityAnalysisResponse(**result)
