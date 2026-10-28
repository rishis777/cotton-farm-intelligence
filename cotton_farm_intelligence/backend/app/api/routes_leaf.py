"""
Cotton Leaf Health and Disease Classification API Routes.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
from io import BytesIO
from datetime import datetime
from PIL import Image
from app.services.model_service import get_leaf_model_service
from app.schemas.schemas import LeafPredictionResponse

router = APIRouter(prefix="/api/leaf", tags=["Cotton Leaf Health (Computer Vision)"])

MAX_IMAGE_SIZE_BYTES = 15 * 1024 * 1024 # 15 MB limit

@router.post("/predict", response_model=LeafPredictionResponse)
async def predict_cotton_leaf_disease(file: UploadFile = File(...)):
    """
    Accepts an uploaded cotton leaf image (JPEG, PNG, WebP) and performs inference
    using the Phase 1 trained MobileNetV2 model.
    Returns predicted class, top-3 probabilities, practical next steps, and academic cautions.
    """
    # 1. Validate MIME type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type '{file.content_type}'. Please upload an image file (JPEG, PNG, or WebP)."
        )

    # 2. Read bytes with size protection
    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Uploaded image exceeds 15 MB limit.")
        
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # 3. Read image with PIL
    try:
        image = Image.open(BytesIO(contents))
        image.verify() # Verify structure
        image = Image.open(BytesIO(contents)) # Reopen for preprocessing
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Corrupted or unreadable image file: {str(e)}")

    # 4. Perform Inference
    model_service = get_leaf_model_service()
    if not model_service.is_loaded:
        raise HTTPException(
            status_code=503, 
            detail=f"Cotton disease classification model unavailable: {model_service.load_error or 'Weights uninitialized'}"
        )

    try:
        prediction_result = model_service.predict(image)
        prediction_result["timestamp"] = datetime.now().isoformat()
        return LeafPredictionResponse(**prediction_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {str(e)}")

@router.get("/model-status")
def get_model_status():
    """Returns runtime model metadata, loaded classes, and Phase 1 test evaluation metrics."""
    service = get_leaf_model_service()
    return {
        "model_loaded": service.is_loaded,
        "device": str(service.device),
        "total_classes": len(service.classes),
        "classes": service.classes,
        "architecture": "MobileNetV2 (ImageNet Pretrained Backbone)",
        "measured_test_accuracy": "89.90% (871 untouched test leaves)",
        "measured_macro_f1": "0.8741",
        "load_error": service.load_error
    }
