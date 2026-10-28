"""
Saved Farms and Analysis History API Routes.
"""

from fastapi import APIRouter, HTTPException, Path as PathParam
from typing import List, Dict, Any
import json
from app.database import get_db_connection
from app.schemas.schemas import SavedFarmCreate, SavedFarmResponse, AnalysisHistoryResponse

router = APIRouter(prefix="/api", tags=["Farms & History"])

@router.get("/farms", response_model=List[SavedFarmResponse])
def get_all_farms():
    """Retrieves all user-saved farm locations from SQLite database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM saved_farms ORDER BY created_at DESC")
        rows = cursor.fetchall()
        
        farms = []
        for r in rows:
            farms.append({
                "id": r["id"],
                "name": r["name"],
                "latitude": r["latitude"],
                "longitude": r["longitude"],
                "taluka": r["taluka"],
                "notes": r["notes"],
                "latest_suitability_category": r["latest_suitability_category"],
                "latest_suitability_score": r["latest_suitability_score"],
                "created_at": str(r["created_at"])
            })
        return farms

@router.post("/farms", response_model=SavedFarmResponse, status_code=201)
def create_farm(farm: SavedFarmCreate):
    """Saves a new farm location with coordinates and optional taluka/notes."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO saved_farms (name, latitude, longitude, taluka, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (farm.name, farm.latitude, farm.longitude, farm.taluka, farm.notes))
        conn.commit()
        farm_id = cursor.lastrowid
        
        cursor.execute("SELECT * FROM saved_farms WHERE id = ?", (farm_id,))
        r = cursor.fetchone()
        return {
            "id": r["id"],
            "name": r["name"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "taluka": r["taluka"],
            "notes": r["notes"],
            "latest_suitability_category": r["latest_suitability_category"],
            "latest_suitability_score": r["latest_suitability_score"],
            "created_at": str(r["created_at"])
        }

@router.delete("/farms/{farm_id}")
def delete_farm(farm_id: int = PathParam(..., ge=1)):
    """Deletes a saved farm location by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM saved_farms WHERE id = ?", (farm_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Farm not found.")
            
        cursor.execute("DELETE FROM saved_farms WHERE id = ?", (farm_id,))
        conn.commit()
        return {"success": True, "message": f"Farm ID {farm_id} successfully deleted."}

@router.get("/analysis-history")
def get_analysis_history(limit: int = 20):
    """Retrieves recent suitability analysis runs with evidence snapshots."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, farm_id, latitude, longitude, timestamp, suitability_category, suitability_score, evidence_json
            FROM analysis_history 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        
        history = []
        for r in rows:
            evidence_data = {}
            try:
                evidence_data = json.loads(r["evidence_json"])
            except Exception:
                pass
            history.append({
                "id": r["id"],
                "farm_id": r["farm_id"],
                "latitude": r["latitude"],
                "longitude": r["longitude"],
                "timestamp": str(r["timestamp"]),
                "suitability_category": r["suitability_category"],
                "suitability_score": r["suitability_score"],
                "evidence": evidence_data
            })
        return history
