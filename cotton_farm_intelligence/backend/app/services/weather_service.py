"""
Weather Service using Open-Meteo API.
Provides current conditions, 7-day forecast, and cotton agronomic climate indicators.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx

WMO_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm"
}

async def fetch_weather_data(lat: float, lon: float) -> Dict[str, Any]:
    """Fetches real-time weather and 7-day forecast from Open-Meteo API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto"
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                current_raw = data.get("current", {})
                daily_raw = data.get("daily", {})
                
                wmo_code = current_raw.get("weather_code", 0)
                cond_text = WMO_CODE_MAP.get(wmo_code, "Fair weather")
                
                temp_curr = current_raw.get("temperature_2m", 28.0)
                rh_curr = current_raw.get("relative_humidity_2m", 50.0)
                
                # Format 7-day forecast
                forecast_list = []
                dates = daily_raw.get("time", [])
                max_temps = daily_raw.get("temperature_2m_max", [])
                min_temps = daily_raw.get("temperature_2m_min", [])
                precips = daily_raw.get("precipitation_sum", [])
                
                for i in range(min(len(dates), 7)):
                    forecast_list.append({
                        "date": dates[i],
                        "temp_max": max_temps[i] if i < len(max_temps) else temp_curr + 4,
                        "temp_min": min_temps[i] if i < len(min_temps) else temp_curr - 4,
                        "precipitation_sum": precips[i] if i < len(precips) else 0.0
                    })
                    
                # Cotton Agronomic Context Analysis
                heat_stress = "High Risk (>38°C)" if temp_curr > 38.0 else ("Moderate" if temp_curr > 34.0 else "Optimal (21-34°C)")
                disease_favorable_rh = rh_curr > 75.0 # High humidity triggers Alternaria / Bacterial Blight
                
                total_7d_rain = sum(f["precipitation_sum"] for f in forecast_list)
                
                return {
                    "latitude": lat,
                    "longitude": lon,
                    "current": {
                        "time": current_raw.get("time", datetime.now().isoformat()),
                        "temperature_2m": temp_curr,
                        "relative_humidity_2m": rh_curr,
                        "precipitation": current_raw.get("precipitation", 0.0),
                        "wind_speed_10m": current_raw.get("wind_speed_10m", 0.0),
                        "weather_code": wmo_code,
                        "condition_text": cond_text
                    },
                    "forecast_7d": forecast_list,
                    "cotton_seasonal_metrics": {
                        "heat_stress_level": heat_stress,
                        "humidity_disease_risk": "Elevated Fungal/Bacterial Risk" if disease_favorable_rh else "Normal/Dry (Low Pathogen Pressure)",
                        "7d_cumulative_precipitation_mm": round(total_7d_rain, 1),
                        "current_agro_season": "Kharif Cotton Maturation / Post-Monsoon Picking",
                        "average_seasonal_rainfall_dhule_mm": "550 - 650 mm (Semi-Arid Zone)"
                    },
                    "source": "Open-Meteo Weather API (CC-BY 4.0)",
                    "timestamp": datetime.now().isoformat()
                }
    except Exception as e:
        print(f"[WEATHER SERVICE ERROR] Falling back to baseline context: {e}")
        
    # Return structured fallback if API fails
    return {
        "latitude": lat,
        "longitude": lon,
        "current": {
            "time": datetime.now().isoformat(),
            "temperature_2m": 30.0,
            "relative_humidity_2m": 45.0,
            "precipitation": 0.0,
            "wind_speed_10m": 5.0,
            "weather_code": 1,
            "condition_text": "Mainly clear (Regional Baseline)"
        },
        "forecast_7d": [],
        "cotton_seasonal_metrics": {
            "heat_stress_level": "Optimal (21-34°C)",
            "humidity_disease_risk": "Normal/Dry (Low Pathogen Pressure)",
            "7d_cumulative_precipitation_mm": 0.0,
            "current_agro_season": "Kharif Cotton Season",
            "average_seasonal_rainfall_dhule_mm": "550 - 650 mm"
        },
        "source": "Open-Meteo API (Offline Fallback - Regional Norms)",
        "timestamp": datetime.now().isoformat()
    }
