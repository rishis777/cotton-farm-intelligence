"""
Cotton Disease Detection - Phase 1: Model Evaluation & Error Analysis
File: src/evaluate_model.py

Objective:
- Evaluate the best trained MobileNetV2 model on the untouched test set.
- Compute Accuracy, Macro-F1, Weighted-F1, Precision, Recall, Confusion Matrix.
- Generate high-resolution confusion matrix heatmap and class-wise performance bar charts.
- Export misclassified-image audit report with true label, predicted label, and confidence score.
- Save full evaluation metrics to 'reports/' and plots to 'outputs/'.
"""

import os
import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from torchvision.models import mobilenet_v2
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support, 
    confusion_matrix, classification_report
)

class CottonTestDataset(Dataset):
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
                    self.samples.append((str(f), self.class_to_idx[cls], cls, f.name))
                    
    def __len__(self):
        return len(self.samples)
        
    def __getitem__(self, idx):
        path, label, cls_name, fname = self.samples[idx]
        with Image.open(path) as raw_img:
            img = raw_img.convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, label, path, cls_name, fname

def evaluate_model(project_root: Path, batch_size: int = 32):
    print("=" * 70)
    print("PHASE 1: UNTOUCHED TEST SET EVALUATION & ERROR ANALYSIS")
    print("=" * 70)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Evaluation Compute Device: {device}")
    
    test_dir = project_root / "data" / "split" / "test"
    models_dir = project_root / "models"
    outputs_dir = project_root / "outputs"
    reports_dir = project_root / "reports"
    
    best_model_path = models_dir / "best_cotton_mobilenetv2.pt"
    mapping_path = models_dir / "class_mapping.json"
    
    if not best_model_path.exists() or not mapping_path.exists():
        print("[ERROR] Trained model checkpoint or class mapping not found in 'models/'.")
        print("Please run 'src/train_model.py' first.")
        sys.exit(1)
        
    with open(mapping_path, "r") as f:
        mapping = json.load(f)
    classes = mapping["classes"]
    num_classes = len(classes)
    
    test_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=mapping["normalization"]["mean"], std=mapping["normalization"]["std"])
    ])
    
    test_dataset = CottonTestDataset(test_dir, transform=test_transforms)
    print(f"Total untouched test samples: {len(test_dataset)} images")
    
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    
    # Load Model
    print(f"Loading checkpoint: {best_model_path.name}...")
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

    all_preds = []
    all_targets = []
    all_probs = []
    misclassified_records = []

    print("Running inference across test batches...")
    softmax = nn.Softmax(dim=1)
    
    with torch.no_grad():
        for images, labels, paths, cls_names, fnames in test_loader:
            images = images.to(device)
            outputs = model(images)
            probs = softmax(outputs).cpu().numpy()
            preds = np.argmax(probs, axis=1)
            
            all_preds.extend(preds)
            all_targets.extend(labels.numpy())
            all_probs.extend(probs)
            
            for i in range(len(preds)):
                if preds[i] != labels[i].item():
                    true_cls = classes[labels[i].item()]
                    pred_cls = classes[preds[i]]
                    conf = float(probs[i][preds[i]])
                    misclassified_records.append({
                        "file_name": fnames[i],
                        "true_class": true_cls,
                        "predicted_class": pred_cls,
                        "model_confidence": round(conf * 100, 2),
                        "file_path": paths[i]
                    })

    all_preds = np.array(all_preds)
    all_targets = np.array(all_targets)

    # Calculate Metrics
    acc = accuracy_score(all_targets, all_preds)
    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
        all_targets, all_preds, average="macro", zero_division=0
    )
    precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(
        all_targets, all_preds, average="weighted", zero_division=0
    )
    
    # Per-class metrics
    precision_per_class, recall_per_class, f1_per_class, support_per_class = precision_recall_fscore_support(
        all_targets, all_preds, average=None, zero_division=0
    )

    print("\n--- Test Set Performance Metrics ---")
    print(f"Overall Accuracy   : {acc * 100:.2f}%")
    print(f"Macro F1-Score     : {f1_macro:.4f}")
    print(f"Weighted F1-Score  : {f1_weighted:.4f}")
    print(f"Macro Precision    : {precision_macro:.4f}")
    print(f"Macro Recall       : {recall_macro:.4f}")
    print(f"Total Misclassified: {len(misclassified_records)} / {len(test_dataset)}")

    print("\n--- Per-Class Detailed Performance ---")
    per_class_data = []
    for i, cls in enumerate(classes):
        p, r, f1, sup = precision_per_class[i], recall_per_class[i], f1_per_class[i], support_per_class[i]
        print(f"  {cls:20s} | Precision: {p:.4f} | Recall: {r:.4f} | F1: {f1:.4f} | Test Count: {sup}")
        per_class_data.append({
            "class": cls,
            "precision": round(float(p), 4),
            "recall": round(float(r), 4),
            "f1_score": round(float(f1), 4),
            "test_sample_count": int(sup)
        })

    # Save Misclassified Report
    misclassified_csv = reports_dir / "misclassified_test_images.csv"
    pd.DataFrame(misclassified_records).to_csv(misclassified_csv, index=False)
    print(f"\n[REPORT SAVED] Misclassified samples saved to: {misclassified_csv}")

    # Save Evaluation JSON
    eval_json = {
        "overall_accuracy": round(float(acc), 4),
        "macro_f1": round(float(f1_macro), 4),
        "weighted_f1": round(float(f1_weighted), 4),
        "macro_precision": round(float(precision_macro), 4),
        "macro_recall": round(float(recall_macro), 4),
        "total_test_images": len(test_dataset),
        "total_misclassified": len(misclassified_records),
        "per_class_metrics": per_class_data
    }
    with open(reports_dir / "evaluation_results.json", "w") as f:
        json.dump(eval_json, f, indent=2)
    print(f"[REPORT SAVED] Full evaluation metrics saved to: {reports_dir / 'evaluation_results.json'}")

    # Plot Confusion Matrix
    cm = confusion_matrix(all_targets, all_preds)
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=classes, yticklabels=classes,
        cbar_kws={'label': 'Number of Images'}
    )
    plt.title("Confusion Matrix - Cotton Disease Test Set", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Predicted Class", fontsize=11, fontweight="bold")
    plt.ylabel("True Class", fontsize=11, fontweight="bold")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    cm_path = outputs_dir / "confusion_matrix.png"
    plt.savefig(cm_path, dpi=300)
    plt.close()
    print(f"[PLOT SAVED] Confusion Matrix saved to: {cm_path}")

    # Plot Per-Class Performance Bar Chart
    df_metrics = pd.DataFrame(per_class_data).set_index("class")
    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(classes))
    width = 0.28
    
    ax.bar([i - width for i in x], df_metrics["precision"], width, label="Precision", color="#2b5c8f")
    ax.bar([i for i in x], df_metrics["recall"], width, label="Recall", color="#f2a900")
    ax.bar([i + width for i in x], df_metrics["f1_score"], width, label="F1-Score", color="#38b000")
    
    ax.set_ylabel("Score (0.0 to 1.0)", fontsize=11, fontweight="bold")
    ax.set_title("Class-wise Precision, Recall, and F1-Score on Test Set", fontsize=14, fontweight="bold", pad=15)
    ax.set_xticks(list(x))
    ax.set_xticklabels(classes, rotation=30, ha="right")
    ax.set_ylim([0, 1.1])
    ax.legend(loc="lower right")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    
    plt.tight_layout()
    metrics_path = outputs_dir / "class_wise_metrics.png"
    plt.savefig(metrics_path, dpi=300)
    plt.close()
    print(f"[PLOT SAVED] Class-wise metrics chart saved to: {metrics_path}")
    print("=" * 70)

if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    evaluate_model(project_root)
