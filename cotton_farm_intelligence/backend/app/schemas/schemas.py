"""
Pydantic Schemas for Cotton Farm Intelligence Dashboard.
Enforces rigorous validation and self-documenting JSON schemas.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class LocationValidationRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude between -90 and 90")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude between -180 and 180")

class LocationValidationResponse(BaseModel):
    valid: bool
    latitude: float
    longitude: float
    in_dhule_district: bool
    in_maharashtra: bool
    taluka_detected: Optional[str] = None
    message: str

class WeatherCurrent(BaseModel):
    time: str
    temperature_2m: float
    relative_humidity_2m: float
    precipitation: float
    wind_speed_10m: float
    weather_code: Optional[int] = None
    condition_text: str

class WeatherForecastDay(BaseModel):
    date: str
    temp_max: float
    temp_min: float
    precipitation_sum: float

class EnvironmentDataResponse(BaseModel):
    latitude: float
    longitude: float
    current: WeatherCurrent
    forecast_7d: List[WeatherForecastDay]
    cotton_seasonal_metrics: Dict[str, Any]
    source: str
    timestamp: str

class SoilDataResponse(BaseModel):
    latitude: float
    longitude: float
    ph: Optional[float] = None
    clay_percentage: Optional[float] = None
    sand_percentage: Optional[float] = None
    silt_percentage: Optional[float] = None
    organic_carbon_g_kg: Optional[float] = None
    soil_type_classification: str
    depth_interval: str
    source: str
    data_status: str # "Observed/SoilGrids API", "Regional Baseline (ICAR-NBSS&LUP)", "Unavailable"
    timestamp: str

class SuitabilityFactor(BaseModel):
    name: str
    factor_group: str # "Climate", "Soil", "Hydrology", "Terrain"
    observed_value: str
    optimal_range: str
    status: str # "Optimal", "Moderate/Constrained", "Suboptimal", "Missing"
    score: float # 0 to 100
    weight: float
    description: str
    data_source: str

class SuitabilityAnalysisRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    farm_name: Optional[str] = "Selected Location"
    irrigation_available: Optional[bool] = False
    notes: Optional[str] = None

class SuitabilityAnalysisResponse(BaseModel):
    latitude: float
    longitude: float
    taluka: Optional[str] = None
    category: str # "Potentially suitable", "Potentially suitable with constraints", "Potentially unsuitable", "Insufficient data"
    overall_score: Optional[float] = None # Only if evidence is sufficient
    evidence_status: str # "Complete Evidence", "Partial Evidence with Constraints", "Insufficient Data"
    factors: List[SuitabilityFactor]
    missing_information: List[str]
    main_constraints: List[str]
    potential_risks: List[str]
    recommended_next_checks: List[str]
    explanation: str
    disclaimer: str
    timestamp: str

class TopPredictionItem(BaseModel):
    disease_class: str
    confidence_percentage: float
    severity_level: str
    symptom_description: str

class LeafPredictionResponse(BaseModel):
    predicted_class: str
    confidence_percentage: float
    top_3_predictions: List[TopPredictionItem]
    model_name: str
    model_version: str
    evaluation_test_accuracy: str
    practical_next_steps: str
    calibration_caution: str
    field_transfer_caution: str
    timestamp: str

class SavedFarmCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    taluka: Optional[str] = None
    notes: Optional[str] = None

class SavedFarmResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    taluka: Optional[str]
    notes: Optional[str]
    latest_suitability_category: Optional[str]
    latest_suitability_score: Optional[float]
    created_at: str

class AnalysisHistoryResponse(BaseModel):
    id: int
    farm_id: Optional[int]
    latitude: float
    longitude: float
    timestamp: str
    suitability_category: str
    suitability_score: Optional[float]
    evidence: Dict[str, Any]
