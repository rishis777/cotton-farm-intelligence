"""
Geocoding and Spatial Verification Service for Dhule District, Maharashtra.
"""

from typing import Dict, Any, Optional, List
import httpx

# Dhule District Bounding Box (Approximate boundaries for verification)
# Lat: 20.60 to 21.65, Lon: 73.78 to 75.25
DHULE_LAT_MIN = 20.60
DHULE_LAT_MAX = 21.65
DHULE_LON_MIN = 73.78
DHULE_LON_MAX = 75.25

# Maharashtra Bounding Box
MAHA_LAT_MIN = 15.60
MAHA_LAT_MAX = 22.10
MAHA_LON_MIN = 72.60
MAHA_LON_MAX = 80.90

# Taluka centroids and rough spatial zones
TALUKAS = {
    "Dhule": {"lat": 20.9042, "lon": 74.7749, "desc": "Central Dhule Taluka - Major cotton market and seed processing hub."},
    "Shirpur": {"lat": 21.3500, "lon": 74.8800, "desc": "Northern Taluka - Tapi basin, high canal/well irrigation and cotton acreage."},
    "Sindkheda": {"lat": 21.2667, "lon": 74.7500, "desc": "North-Central Taluka - Rich black alluvial soil along Tapi and Panzara rivers."},
    "Sakri": {"lat": 20.9333, "lon": 74.3167, "desc": "Western Taluka - Rainfed Kharif cotton with undulating terrain."}
}

def validate_coordinates(lat: float, lon: float) -> Dict[str, Any]:
    """Validates coordinates and determines administrative context."""
    if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
        return {
            "valid": False,
            "latitude": lat,
            "longitude": lon,
            "in_dhule_district": False,
            "in_maharashtra": False,
            "taluka_detected": None,
            "message": "Coordinates are mathematically invalid. Latitude must be in [-90, 90] and Longitude in [-180, 180]."
        }

    in_dhule = (DHULE_LAT_MIN <= lat <= DHULE_LAT_MAX) and (DHULE_LON_MIN <= lon <= DHULE_LON_MAX)
    in_maha = (MAHA_LAT_MIN <= lat <= MAHA_LAT_MAX) and (MAHA_LON_MIN <= lon <= MAHA_LON_MAX)

    detected_taluka = None
    if in_dhule:
        # Nearest taluka centroid
        closest = None
        min_dist = float("inf")
        for t_name, t_data in TALUKAS.items():
            dist = ((lat - t_data["lat"])**2 + (lon - t_data["lon"])**2)**0.5
            if dist < min_dist:
                min_dist = dist
                closest = t_name
        detected_taluka = closest

    if in_dhule:
        msg = f"Valid coordinates located inside Dhule District (near {detected_taluka} Taluka)."
    elif in_maha:
        msg = "Valid coordinates inside Maharashtra, but outside Dhule District boundaries."
    else:
        msg = "Valid global coordinates, but outside Maharashtra cotton-growing belt."

    return {
        "valid": True,
        "latitude": lat,
        "longitude": lon,
        "in_dhule_district": in_dhule,
        "in_maharashtra": in_maha,
        "taluka_detected": detected_taluka,
        "message": msg
    }

async def search_location_nominatim(query: str) -> List[Dict[str, Any]]:
    """Searches locations using OpenStreetMap Nominatim with safety timeout."""
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "CottonFarmIntelligence-DhuleAcademicProject/1.0 (academic-research)"}
    params = {"q": query, "format": "json", "limit": 5, "addressdetails": 1}
    
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(url, params=params, headers=headers)
            if resp.status_code == 200:
                results = []
                for item in resp.json():
                    results.append({
                        "display_name": item.get("display_name"),
                        "latitude": float(item.get("lat")),
                        "longitude": float(item.get("lon")),
                        "type": item.get("type"),
                        "importance": item.get("importance")
                    })
                return results
    except Exception as e:
        print(f"[GEOCODING NOTICE] Nominatim lookup fallback: {e}")
        
    # Fallback to local Dhule known points if offline
    q_lower = query.lower()
    matches = []
    for t_name, data in TALUKAS.items():
        if t_name.lower() in q_lower or "dhule" in q_lower:
            matches.append({
                "display_name": f"{t_name}, Dhule District, Maharashtra, India",
                "latitude": data["lat"],
                "longitude": data["lon"],
                "type": "administrative",
                "importance": 0.8
            })
    return matches
