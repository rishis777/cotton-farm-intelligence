"""
Cotton Disease Detection - Phase 1: New Image Prediction CLI
File: src/predict_image.py

Objective:
- Accept a single image path from CLI argument.
- Validate image readability and file existence.
- Apply exact MobileNetV2 normalization and sizing.
- Return Top-1 prediction, confidence score, and Top-3 probabilities.
- Display explicit scientific warnings regarding score calibration and Dhule regional field transfer.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from PIL import Image

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import mobilenet_v2

def predict_single_image(image_path_str: str, project_root: Path):
    img_path = Path(image_path_str)
    
    if not img_path.exists():
        print(f"\n[ERROR] Provided image file does not exist: {img_path}")
        sys.exit(1)
        
    models_dir = project_root / "models"
    best_model_path = models_dir / "best_cotton_mobilenetv2.pt"
    mapping_path = models_dir / "class_mapping.json"
    
    if not best_model_path.exists() or not mapping_path.exists():
        print("\n[ERROR] Trained model checkpoint or class mapping not found in 'models/'.")
        print("Please train the model first by running 'python src/train_model.py'.")
        sys.exit(1)

    # Load Class Mapping
    with open(mapping_path, "r") as f:
        mapping = json.load(f)
    classes = mapping["classes"]
    num_classes = len(classes)

    # Load and Preprocess Image
    try:
        with Image.open(img_path) as raw_img:
            img = raw_img.convert("RGB")
    except Exception as e:
        print(f"\n[ERROR] Unable to read or parse image file: {e}")
        sys.exit(1)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=mapping["normalization"]["mean"], std=mapping["normalization"]["std"])
    ])
    
    input_tensor = preprocess(img).unsqueeze(0).to(device) # Shape: [1, 3, 224, 224]

    # Load Model
    model = mobilenet_v2(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, num_classes)
    )
    checkpoint = torch.load(best_model_path, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model = model.to(device)
    model.eval()

    # Inference
    softmax = nn.Softmax(dim=1)
    with torch.no_grad():
        logits = model(input_tensor)
        probs = softmax(logits)[0]

    top_probs, top_indices = torch.topk(probs, k=min(3, num_classes))
    top_probs = top_probs.cpu().numpy()
    top_indices = top_indices.cpu().numpy()

    top_class = classes[top_indices[0]]
    top_conf = float(top_probs[0]) * 100

    print("\n" + "=" * 65)
    print("COTTON LEAF DISEASE INFERENCE RESULT")
    print("=" * 65)
    print(f"Target Image   : {img_path.resolve()}")
    print(f"Primary Class  : {top_class}")
    print(f"Model Score    : {top_conf:.2f}%")
    
    print("\n--- Top-3 Model Predictions ---")
    for rank, (idx, prob) in enumerate(zip(top_indices, top_probs), start=1):
        print(f"  #{rank}: {classes[idx]:20s} -> {prob * 100:.2f}%")

    print("\n" + "-" * 65)
    print("CRITICAL SCIENTIFIC & FIELD CAUTIONS:")
    print(" 1. Probability Calibration: The percentage score represents the model's")
    print("    softmax activation, which can be uncalibrated or overconfident.")
    print(" 2. Dhule Field Generalization: This model is trained on an online")
    print("    dataset. Real-world cotton leaves from Dhule district farms (Maharashtra)")
    print("    may encounter varying soil, sunlight, weather, camera angles, and pests.")
    print("    Local agronomic testing is required prior to real-world deployment.")
    print("=" * 65 + "\n")

    return {
        "top_class": top_class,
        "confidence": top_conf,
        "top_3": [(classes[idx], float(prob)) for idx, prob in zip(top_indices, top_probs)]
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict Cotton Leaf Disease using MobileNetV2")
    parser.add_argument("--image", type=str, required=True, help="Path to the cotton leaf image")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    proj_root = script_dir.parent
    predict_single_image(args.image, proj_root)
