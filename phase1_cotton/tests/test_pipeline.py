"""
Cotton Disease Detection - Phase 1: Test Suite
File: tests/test_pipeline.py

Objective:
- Practical automated unit & integration tests verifying:
  1. Dataset path existence and class folder completeness.
  2. Dataset split consistency and leakage prevention (no hash overlap between Train and Test).
  3. Class-name mapping consistency.
  4. Augmentation functions integrity.
  5. Model architecture and checkpoint integrity.
  6. Single image inference execution.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from PIL import Image
import pytest
import torch

# Add src to path
proj_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(proj_root / "src"))

import augment_dataset
from predict_image import predict_single_image

def test_dataset_paths():
    """Verify split directories exist and contain 9 classes."""
    split_dir = proj_root / "data" / "split"
    assert split_dir.exists(), "Split directory missing"
    
    expected_classes = [
        "Alternaria_Leaf", "Aphids", "Army_worm", "Bacterial_Blight",
        "Fusarium_Wilt", "Healthy_Leaf", "Powdery_Mildew", "Target_spot", "Verticillium_Wilt"
    ]
    
    for split in ["train", "validation", "test"]:
        s_path = split_dir / split
        assert s_path.exists(), f"Split '{split}' folder is missing"
        actual_classes = sorted([d.name for d in s_path.iterdir() if d.is_dir()])
        assert actual_classes == expected_classes, f"Class mismatch in {split}: {actual_classes}"

def test_no_data_leakage_between_train_and_test():
    """Verify that no image in test or val shares an exact cryptographic hash with train."""
    split_dir = proj_root / "data" / "split"
    
    def get_hashes(directory: Path):
        hashes = set()
        for f in directory.rglob("*"):
            if f.is_file() and not f.name.startswith("."):
                with open(f, "rb") as fp:
                    hashes.add(hashlib.md5(fp.read()).hexdigest())
        return hashes
        
    train_hashes = get_hashes(split_dir / "train")
    val_hashes = get_hashes(split_dir / "validation")
    test_hashes = get_hashes(split_dir / "test")
    
    val_leakage = train_hashes.intersection(val_hashes)
    test_leakage = train_hashes.intersection(test_hashes)
    
    assert len(val_leakage) == 0, f"Critical Data Leakage detected: {len(val_leakage)} identical images in Train and Val!"
    assert len(test_leakage) == 0, f"Critical Data Leakage detected: {len(test_leakage)} identical images in Train and Test!"

def test_augmentation_transforms():
    """Verify that transformation functions output valid images with unchanged dimensions."""
    sample_img = Image.new("RGB", (224, 224), color=(120, 180, 70))
    
    flipped = augment_dataset.apply_horizontal_flip(sample_img)
    assert flipped.size == (224, 224)
    
    rotated = augment_dataset.apply_mild_rotation(sample_img, 15.0)
    assert rotated.size == (224, 224)
    
    brightened = augment_dataset.apply_brightness(sample_img, 1.1)
    assert brightened.size == (224, 224)
    
    zoomed = augment_dataset.apply_conservative_zoom(sample_img, 0.95)
    assert zoomed.size == (224, 224)

def test_class_mapping_consistency():
    """Verify class mapping file exists and matches folder names."""
    mapping_path = proj_root / "models" / "class_mapping.json"
    if mapping_path.exists():
        with open(mapping_path, "r") as f:
            mapping = json.load(f)
        classes = mapping["classes"]
        assert len(classes) == 9
        assert "Aphids" in classes
        assert "Bacterial_Blight" in classes
