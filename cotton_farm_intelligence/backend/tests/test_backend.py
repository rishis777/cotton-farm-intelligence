"""
Backend Automated Test Suite for Cotton Farm Intelligence Dashboard.
Tests endpoints, schemas, services, database persistence, and error handling.
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add app to path
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

from app.main import app

client = TestClient(app)

def test_health_check():
    """Verify health endpoint returns 200 and healthy status."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["region"] == "Dhule District, Maharashtra, India"
    assert data["default_coordinates"]["latitude"] == 20.9042

def test_location_validation_dhule():
    """Verify Dhule coordinates validation returns in_dhule_district=True."""
    resp = client.get("/api/location/validate?lat=20.9042&lon=74.7749")
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["in_dhule_district"] is True
    assert data["taluka_detected"] == "Dhule"

def test_location_validation_out_of_bounds():
    """Verify out-of-bounds coordinates return 422 Unprocessable Entity."""
    resp = client.get("/api/location/validate?lat=95.0&lon=74.7749")
    assert resp.status_code == 422

def test_environment_endpoint():
    """Verify environment endpoint retrieves current conditions and forecast."""
    resp = client.get("/api/environment?lat=20.9042&lon=74.7749")
    assert resp.status_code == 200
    data = resp.json()
    assert "current" in data
    assert "temperature_2m" in data["current"]
    assert "cotton_seasonal_metrics" in data

def test_soil_endpoint():
    """Verify soil endpoint returns pH and texture properties."""
    resp = client.get("/api/soil?lat=20.9042&lon=74.7749")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ph"] is not None
    assert data["clay_percentage"] is not None
    assert "Vertisol" in data["soil_type_classification"] or "Clay" in data["soil_type_classification"]

def test_suitability_analysis():
    """Verify suitability analysis returns evidence-based categorization."""
    payload = {
        "latitude": 20.9042,
        "longitude": 74.7749,
        "irrigation_available": True
    }
    resp = client.post("/api/suitability/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["category"] in [
        "Potentially suitable", 
        "Potentially suitable with constraints", 
        "Potentially unsuitable", 
        "Insufficient data"
    ]
    assert len(data["factors"]) >= 4
    assert data["overall_score"] is not None

def test_model_status():
    """Verify computer vision model service status and class metadata."""
    resp = client.get("/api/leaf/model-status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["model_loaded"] is True
    assert data["total_classes"] == 9
    assert "Alternaria_Leaf" in data["classes"]
    assert "Healthy_Leaf" in data["classes"]

def test_saved_farms_crud():
    """Verify creating, listing, and deleting a saved farm."""
    # 1. Create
    farm_data = {
        "name": "Test Experimental Plot",
        "latitude": 20.9100,
        "longitude": 74.7800,
        "taluka": "Dhule",
        "notes": "Automated unit test farm"
    }
    post_resp = client.post("/api/farms", json=farm_data)
    assert post_resp.status_code == 201
    created = post_resp.json()
    farm_id = created["id"]
    assert created["name"] == "Test Experimental Plot"

    # 2. Verify in list
    list_resp = client.get("/api/farms")
    assert list_resp.status_code == 200
    farm_ids = [f["id"] for f in list_resp.json()]
    assert farm_id in farm_ids

    # 3. Delete
    del_resp = client.delete(f"/api/farms/{farm_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True
