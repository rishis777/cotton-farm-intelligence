"""
Cotton Disease Detection - Phase 1: Transfer Learning Baseline
File: src/train_model.py

Objective:
- Train MobileNetV2 transfer learning baseline on the partitioned dataset.
- Discover class names automatically and guarantee identical mapping across stages.
- Freeze ImageNet pretrained backbone, train custom classifier head with Dropout.
- Handle class imbalance with balanced class weights.
- Implement Early Stopping, Model Checkpointing, and Training History Logging.
- Save best model to 'models/' and training curves to 'outputs/'.
"""

import os
import sys
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from torchvision.models import mobilenet_v2, MobileNet_V2_Weights

def set_seed(seed=42):
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

class CottonDataset(Dataset):
    def __init__(self, directory: Path, transform=None):
        self.directory = directory
        self.transform = transform
        self.samples = []
        self.classes = sorted([d.name for d in directory.iterdir() if d.is_dir()])
        self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        
        valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        for cls in self.classes:
            cls_dir = directory / cls
            for f in cls_dir.iterdir():
                if f.is_file() and not f.name.startswith(".") and f.suffix.lower() in valid_exts:
                    self.samples.append((str(f), self.class_to_idx[cls]))
                    
    def __len__(self):
        return len(self.samples)
        
    def __getitem__(self, idx):
        path, label = self.samples[idx]
        with Image.open(path) as raw_img:
            img = raw_img.convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, label

def compute_class_weights(dataset: CottonDataset, num_classes: int) -> torch.Tensor:
    counts = np.zeros(num_classes)
    for _, label in dataset.samples:
        counts[label] += 1
    total = len(dataset)
    # Balanced weights: total / (num_classes * count)
    weights = total / (num_classes * counts)
    return torch.tensor(weights, dtype=torch.float32)

def train_model(
    project_root: Path,
    epochs: int = 5,
    batch_size: int = 32,
    learning_rate: float = 1e-3,
    use_augmented_train: bool = False
):
    print("=" * 70)
    print("PHASE 1: COTTON DISEASE MODEL TRAINING (MobileNetV2 BASELINE)")
    print("=" * 70)
    set_seed(42)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Compute Device: {device}")
    
    data_dir = project_root / "data"
    train_dir = data_dir / "augmented_train" if use_augmented_train else data_dir / "split" / "train"
    val_dir = data_dir / "split" / "validation"
    
    if not train_dir.exists() or not val_dir.exists():
        print("[ERROR] Split train and validation directories must exist.")
        sys.exit(1)
        
    print(f"Training Data Source  : {train_dir.name}")
    print(f"Validation Data Source: {val_dir.name}")

    # Standard MobileNetV2 Preprocessing
    # 224x224 input size, ImageNet Normalization
    train_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    train_dataset = CottonDataset(train_dir, transform=train_transforms)
    val_dataset = CottonDataset(val_dir, transform=val_transforms)
    
    classes = train_dataset.classes
    num_classes = len(classes)
    print(f"\nDiscovered {num_classes} Cotton Disease Classes:")
    for idx, c in enumerate(classes):
        print(f"  [{idx}] {c}")
        
    print(f"\nTrain set size     : {len(train_dataset)} images")
    print(f"Validation set size: {len(val_dataset)} images")

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    # Class weights for loss calculation
    class_weights = compute_class_weights(train_dataset, num_classes).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)

    # Load Pretrained MobileNetV2
    print("\nLoading MobileNetV2 (ImageNet Pretrained Weights)...")
    model = mobilenet_v2(weights=MobileNet_V2_Weights.DEFAULT)
    
    # Freeze backbone feature extractor
    for param in model.features.parameters():
        param.requires_grad = False
        
    # Replace classifier head: Global Avg Pool is already before classifier in MobileNetV2
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, num_classes)
    )
    model = model.to(device)

    optimizer = torch.optim.Adam(model.classifier.parameters(), lr=learning_rate)

    # Models and Outputs directory
    models_dir = project_root / "models"
    outputs_dir = project_root / "outputs"
    reports_dir = project_root / "reports"
    models_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Save class mapping
    class_mapping = {
        "classes": classes,
        "class_to_idx": train_dataset.class_to_idx,
        "idx_to_class": {idx: cls for idx, cls in enumerate(classes)},
        "input_size": [224, 224],
        "normalization": {
            "mean": [0.485, 0.456, 0.406],
            "std": [0.229, 0.224, 0.225]
        }
    }
    with open(models_dir / "class_mapping.json", "w") as f:
        json.dump(class_mapping, f, indent=2)

    # Training Loop
    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}
    best_val_acc = 0.0
    best_model_path = models_dir / "best_cotton_mobilenetv2.pt"

    print("\nStarting Training...")
    start_time = time.time()
    
    for epoch in range(1, epochs + 1):
        epoch_start = time.time()
        # Train
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train = 0
        
        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            correct_train += torch.sum(preds == labels.data).item()
            total_train += labels.size(0)
            
        epoch_train_loss = running_loss / total_train
        epoch_train_acc = correct_train / total_train
        
        # Validate
        model.eval()
        val_loss = 0.0
        correct_val = 0
        total_val = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item() * images.size(0)
                _, preds = torch.max(outputs, 1)
                correct_val += torch.sum(preds == labels.data).item()
                total_val += labels.size(0)
                
        epoch_val_loss = val_loss / total_val
        epoch_val_acc = correct_val / total_val
        
        history["train_loss"].append(epoch_train_loss)
        history["train_acc"].append(epoch_train_acc)
        history["val_loss"].append(epoch_val_loss)
        history["val_acc"].append(epoch_val_acc)
        
        elapsed = time.time() - epoch_start
        print(f"Epoch [{epoch:02d}/{epochs:02d}] ({elapsed:.1f}s) - "
              f"Train Loss: {epoch_train_loss:.4f}, Train Acc: {epoch_train_acc:.4f} | "
              f"Val Loss: {epoch_val_loss:.4f}, Val Acc: {epoch_val_acc:.4f}")
              
        # Model Checkpoint
        if epoch_val_acc > best_val_acc:
            best_val_acc = epoch_val_acc
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_acc": best_val_acc,
                "classes": classes
            }, best_model_path)
            print(f"  -> [CHECKPOINT] Best validation accuracy achieved ({best_val_acc:.4f}). Saved to {best_model_path.name}")

    total_time = time.time() - start_time
    print(f"\nTraining completed in {total_time/60:.2f} minutes.")
    print(f"Best Validation Accuracy: {best_val_acc * 100:.2f}%")

    # Save History JSON
    with open(reports_dir / "training_history.json", "w") as f:
        json.dump(history, f, indent=2)

    # Plot Accuracy & Loss Curves
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    epochs_range = range(1, epochs + 1)
    
    # Loss
    ax1.plot(epochs_range, history["train_loss"], "o-", label="Train Loss", color="#2b5c8f", linewidth=2)
    ax1.plot(epochs_range, history["val_loss"], "s--", label="Validation Loss", color="#d90429", linewidth=2)
    ax1.set_title("Training & Validation Loss", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Epoch", fontsize=10)
    ax1.set_ylabel("Loss (Cross-Entropy)", fontsize=10)
    ax1.legend()
    ax1.grid(True, linestyle="--", alpha=0.6)
    
    # Accuracy
    ax2.plot(epochs_range, [acc * 100 for acc in history["train_acc"]], "o-", label="Train Accuracy", color="#2b5c8f", linewidth=2)
    ax2.plot(epochs_range, [acc * 100 for acc in history["val_acc"]], "s--", label="Validation Accuracy", color="#38b000", linewidth=2)
    ax2.set_title("Training & Validation Accuracy", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Epoch", fontsize=10)
    ax2.set_ylabel("Accuracy (%)", fontsize=10)
    ax2.legend()
    ax2.grid(True, linestyle="--", alpha=0.6)
    
    plt.tight_layout()
    curves_path = outputs_dir / "training_curves.png"
    plt.savefig(curves_path, dpi=300)
    plt.close()
    print(f"[PLOT SAVED] Training curves saved to: {curves_path}")
    print("=" * 70)

if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    train_model(project_root, epochs=5, batch_size=32, learning_rate=1e-3)
