"""
Agronomic Suitability Engine for Cotton Cultivation in Dhule, Maharashtra.
Evaluates evidence against documented ICAR-CICR and MPKV Rahuri cotton agronomic guidelines.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from app.services.weather_service import fetch_weather_data
from app.services.soil_service import fetch_soil_data
from app.services.geocoding_service import validate_coordinates

# Official ICAR-CICR (Central Institute for Cotton Research) Agronomic Benchmarks
# 1. Temperature: Ideal vegetative 21°C - 30°C, flowering 25°C - 34°C. Severe limit > 38°C or < 15°C.
# 2. Soil pH: Optimal 6.5 - 8.5 (Cotton tolerates mild salinity/alkalinity). Suboptimal < 5.8 or > 8.8.
# 3. Soil Texture: Clay fraction > 40% (Vertisol / Black cotton soil) yields high moisture retention.
# 4. Seasonal Rainfall: Kharif cotton requires 500 - 800 mm. In Dhule (semi-arid, 550-650mm), rainfed cultivation
#    faces terminal moisture stress without supplemental drip/well irrigation.
# 5. Drainage: Requires moderate-to-well drained land. Heavy waterlogging leads to root suffocation and Fusarium wilt.

async def evaluate_cotton_suitability(
    lat: float, 
    lon: float, 
    irrigation_available: bool = False,
    user_notes: Optional[str] = None
) -> Dict[str, Any]:
    
    geo_check = validate_coordinates(lat, lon)
    if not geo_check["valid"]:
        return {
            "latitude": lat,
            "longitude": lon,
            "taluka": None,
            "category": "Insufficient data",
            "overall_score": None,
            "evidence_status": "Invalid Coordinates",
            "factors": [],
            "missing_information": ["Coordinates are outside mathematically valid geospatial bounds."],
            "main_constraints": ["Invalid geospatial reference."],
            "potential_risks": ["Cannot map environmental indicators."],
            "recommended_next_checks": ["Enter valid latitude [-90, 90] and longitude [-180, 180]."],
            "explanation": "Assessment halted because the input coordinates are outside geographic bounds.",
            "disclaimer": "Preliminary decision support tool based on regional spatial models, not a substitute for local agronomic soil testing.",
            "timestamp": datetime.now().isoformat()
        }

    # Fetch Environmental Evidence asynchronously
    weather = await fetch_weather_data(lat, lon)
    soil = await fetch_soil_data(lat, lon)

    factors = []
    constraints = []
    risks = []
    missing_info = []
    
    # 1. Temperature Suitability Evaluation
    curr_temp = weather["current"]["temperature_2m"]
    if 21.0 <= curr_temp <= 34.0:
        t_score = 92.0
        t_status = "Optimal"
        t_desc = f"Observed temperature ({curr_temp}°C) is within ideal physiological range (21-34°C) for cotton growth."
    elif 34.0 < curr_temp <= 38.0:
        t_score = 75.0
        t_status = "Moderate/Constrained"
        t_desc = f"Observed temperature ({curr_temp}°C) is warm; mild heat stress may occur during peak noon hours."
        constraints.append("Elevated ambient temperature; ensure adequate root zone moisture.")
    elif curr_temp > 38.0:
        t_score = 45.0
        t_status = "Suboptimal"
        t_desc = f"High temperature ({curr_temp}°C) exceeds 38°C threshold, risking square and boll drying."
        constraints.append("Extreme heat stress (>38°C) poses boll shedding danger.")
        risks.append("Premature boll drop and reduced pollen viability.")
    else:
        t_score = 55.0
        t_status = "Suboptimal"
        t_desc = f"Cool temperature ({curr_temp}°C) slows cotton seedling germination and boll development."
        constraints.append("Low temperature below 20°C slows metabolic rate.")

    factors.append({
        "name": "Ambient Temperature",
        "factor_group": "Climate",
        "observed_value": f"{curr_temp} °C",
        "optimal_range": "21.0 - 34.0 °C",
        "status": t_status,
        "score": t_score,
        "weight": 0.25,
        "description": t_desc,
        "data_source": weather["source"]
    })

    # 2. Soil pH Evaluation
    soil_ph = soil.get("ph")
    if soil_ph is not None:
        if 6.8 <= soil_ph <= 8.3:
            ph_score = 95.0
            ph_status = "Optimal"
            ph_desc = f"Soil pH ({soil_ph}) is optimal for cotton nutrient absorption in typical Maharashtra Vertisols."
        elif (6.0 <= soil_ph < 6.8) or (8.3 < soil_ph <= 8.6):
            ph_score = 78.0
            ph_status = "Moderate/Constrained"
            ph_desc = f"Soil pH ({soil_ph}) is acceptable but requires micronutrient monitoring (Zinc/Iron availability)."
            constraints.append(f"Soil pH of {soil_ph} may restrict phosphorus or zinc uptake.")
        else:
            ph_score = 40.0
            ph_status = "Suboptimal"
            ph_desc = f"Soil pH ({soil_ph}) is outside desirable range. High alkalinity or acidity impairs cotton taproot."
            constraints.append(f"Suboptimal soil pH ({soil_ph}) requires gypsum or lime reclamation.")
            risks.append("Severe nutrient lockup and stunted root architecture.")
    else:
        ph_score = 50.0
        ph_status = "Missing"
        ph_desc = "Point-level soil pH could not be retrieved from spatial database."
        missing_info.append("Laboratory topsoil pH measurement.")

    factors.append({
        "name": "Soil pH",
        "factor_group": "Soil",
        "observed_value": f"{soil_ph}" if soil_ph else "Unavailable",
        "optimal_range": "6.5 - 8.5 (Mild Alkaline Vertisol)",
        "status": ph_status,
        "score": ph_score,
        "weight": 0.20,
        "description": ph_desc,
        "data_source": soil["source"]
    })

    # 3. Soil Texture (Clay Fraction & Vertisol Nature)
    clay = soil.get("clay_percentage")
    if clay is not None:
        if clay >= 45.0:
            clay_score = 90.0
            clay_status = "Optimal"
            clay_desc = f"Heavy clay texture ({clay}%) is characteristic of classic Black Cotton Soil (Regur/Vertisol) with high water retention."
        elif 30.0 <= clay < 45.0:
            clay_score = 80.0
            clay_status = "Moderate/Constrained"
            clay_desc = f"Medium clay loam ({clay}%) provides good drainage with moderate water retention."
        else:
            clay_score = 50.0
            clay_status = "Suboptimal"
            clay_desc = f"Low clay fraction ({clay}%) indicates sandy/gravelly soil with low water holding capacity."
            constraints.append("Light soil texture requires frequent irrigation intervals.")
            risks.append("Rapid drought stress in dry spells.")
    else:
        clay_score = 50.0
        clay_status = "Missing"
        clay_desc = "Soil texture data unavailable."
        missing_info.append("Soil textural fraction analysis.")

    factors.append({
        "name": "Soil Texture & Clay Fraction",
        "factor_group": "Soil",
        "observed_value": f"{clay}% Clay" if clay else "Unavailable",
        "optimal_range": ">= 40.0% Clay (Vertisol)",
        "status": clay_status,
        "score": clay_score,
        "weight": 0.20,
        "description": clay_desc,
        "data_source": soil["source"]
    })

    # 4. Water Availability & Irrigation Context
    if irrigation_available:
        water_score = 90.0
        water_status = "Optimal"
        water_desc = "Assured irrigation (well / canal / drip) mitigates dry spell risks in Dhule's semi-arid rainfall regime."
    else:
        water_score = 65.0
        water_status = "Moderate/Constrained"
        water_desc = "Rainfed cultivation dependent solely on monsoon (Kharif). Dhule's 550-650 mm rainfall has dry spell vulnerability."
        constraints.append("Rainfed cultivation: Vulnerable to 15-20 day monsoon dry spells during flowering/boll stage.")
        risks.append("Terminal moisture stress leading to low boll weight and lower staple length.")

    factors.append({
        "name": "Moisture & Irrigation Support",
        "factor_group": "Hydrology",
        "observed_value": "Assured Irrigation" if irrigation_available else "Rainfed (Kharif Monsoon Dependent)",
        "optimal_range": "Supplemental irrigation or 650-800 mm distributed rainfall",
        "status": water_status,
        "score": water_score,
        "weight": 0.20,
        "description": water_desc,
        "data_source": "User Farm Input & Dhule Regional Precipitation Pattern"
    })

    # 5. Agro-Climatic Zone & Location Context
    if geo_check["in_dhule_district"]:
        taluka = geo_check["taluka_detected"] or "Dhule"
        zone_score = 88.0
        zone_status = "Optimal"
        zone_desc = f"Located in {taluka} Taluka within Khandesh cotton agro-climatic zone with established cotton procurement infrastructure."
    elif geo_check["in_maharashtra"]:
        taluka = "Maharashtra State"
        zone_score = 75.0
        zone_status = "Moderate/Constrained"
        zone_desc = "Located in Maharashtra, but outside primary Khandesh district boundaries. Verify local taluka crop calendar."
        constraints.append("Outside primary Dhule cotton cluster; verify regional micro-climate.")
    else:
        taluka = "Outside Maharashtra"
        zone_score = 45.0
        zone_status = "Suboptimal"
        zone_desc = "Location is outside Maharashtra. Regional agro-climatic baseline may differ significantly."
        constraints.append("Non-Maharashtra agro-ecological zone.")

    factors.append({
        "name": "Regional Agro-Climatic Zone",
        "factor_group": "Terrain & Zone",
        "observed_value": f"{taluka} Region",
        "optimal_range": "Khandesh Cotton Belt (Dhule, Jalgaon, Nandurbar)",
        "status": zone_status,
        "score": zone_score,
        "weight": 0.15,
        "description": zone_desc,
        "data_source": "Administrative Bounding Boundary Data"
    })

    # Weighted Overall Score Calculation
    total_score = sum(f["score"] * f["weight"] for f in factors)
    overall_score = round(total_score, 1)

    # Categorization logic adhering to prompt requirements:
    # "Potentially suitable", "Potentially suitable with constraints", "Potentially unsuitable", "Insufficient data"
    if len(missing_info) >= 3:
        category = "Insufficient data"
        evidence_status = "Insufficient Data"
        overall_score = None
        explanation = "Multiple critical environmental variables could not be verified. Farm suitability cannot be reliably established."
    elif overall_score >= 85.0 and len(constraints) == 0:
        category = "Potentially suitable"
        evidence_status = "Complete Evidence"
        explanation = "Climate, Vertisol soil texture, and moisture conditions align favorably with standard cotton agronomic requirements."
    elif overall_score >= 65.0:
        category = "Potentially suitable with constraints"
        evidence_status = "Partial Evidence with Constraints"
        explanation = f"Location is generally viable for cotton, but presents specific constraints ({', '.join(constraints[:2])})."
    else:
        category = "Potentially unsuitable"
        evidence_status = "Documented Agronomic Mismatches"
        explanation = "Environmental indicators show severe deviations from cotton physiological tolerance thresholds."

    # Practical Next Checks (Official Agricultural Recommendations)
    next_checks = [
        "Conduct a certified local Krishi Vigyan Kendra (KVK Dhule) laboratory soil test for N-P-K, micronutrients (Zn, Fe), and electrical conductivity.",
        "Ensure field surface drainage channels are prepared before Kharif onset to prevent waterlogging in deep black Vertisol soils.",
        "Adopt drip irrigation or broad bed furrow (BBF) planting to mitigate mid-season dry spell risks.",
        "Consult MPKV Rahuri (Mahatma Phule Krishi Vidyapeeth) package of practices for recommended Bt-cotton hybrids suited for Dhule talukas."
    ]

    return {
        "latitude": lat,
        "longitude": lon,
        "taluka": geo_check["taluka_detected"],
        "category": category,
        "overall_score": overall_score,
        "evidence_status": evidence_status,
        "factors": factors,
        "missing_information": missing_info,
        "main_constraints": constraints if constraints else ["No severe environmental constraints detected."],
        "potential_risks": risks if risks else ["Standard seasonal pest pressure (bollworms, aphids) during high humidity spells."],
        "recommended_next_checks": next_checks,
        "explanation": explanation,
        "disclaimer": "This assessment is a preliminary decision-support guide based on regional agro-climatic data and satellite estimates. It does not replace field soil testing, ground water surveys, or localized plant pathology consultations.",
        "timestamp": datetime.now().isoformat()
    }
