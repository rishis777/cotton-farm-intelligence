"""
Cotton Disease Detection - Phase 1: Dataset Inspection
File: src/inspect_dataset.py

Objective:
- Discover actual folder structures in 'Original Dataset' and 'Augmented Dataset'.
- Count valid images per class (ignoring OS files like .DS_Store).
- Detect class name mismatches between directories.
- Export findings to CSV in 'reports/' and a comparative plot in 'outputs/'.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def inspect_dataset(data_root: Path, output_dir: Path, report_dir: Path):
    print("=" * 70)
    print("PHASE 1: COTTON DATASET DISCOVERY & VERIFICATION")
    print("=" * 70)
    print(f"Target Data Root: {data_root.resolve()}")
    
    if not data_root.exists():
        print(f"[ERROR] Data root does not exist: {data_root}")
        sys.exit(1)
        
    orig_dir = data_root / "Original Dataset"
    aug_dir = data_root / "Augmented Dataset"
    
    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}
    
    def scan_dir(target_dir: Path, dataset_name: str):
        if not target_dir.exists():
            print(f"[WARNING] Directory not found: {target_dir}")
            return {}
        
        class_counts = {}
        for item in sorted(target_dir.iterdir()):
            if item.is_dir():
                # Count only valid images
                img_files = [
                    f for f in item.iterdir()
                    if f.is_file() and f.suffix.lower() in valid_extensions and not f.name.startswith(".")
                ]
                class_counts[item.name] = len(img_files)
        return class_counts

    orig_counts = scan_dir(orig_dir, "Original Dataset")
    aug_counts = scan_dir(aug_dir, "Augmented Dataset")
    
    # Class mapping / normalization to compare side by side
    canonical_mapping = {
        "Alternaria Leaf Spot": "Alternaria Leaf",
        "Alternaria_Leaf": "Alternaria Leaf",
        "Aphids": "Aphids",
        "Army_worm": "Army Worm",
        "Bacterial_Blight": "Bacterial Blight",
        "Fusarium Wilt": "Fusarium Wilt",
        "Fusarium_Wilt": "Fusarium Wilt",
        "Healthy": "Healthy Leaf",
        "Healthy_Leaf": "Healthy Leaf",
        "Powdery_Mildew": "Powdery Mildew",
        "Target_spot": "Target Spot",
        "Verticillium Wilt": "Verticillium Wilt",
        "Verticillium_Wilt": "Verticillium Wilt",
    }
    
    print("\n--- Detected Original Dataset Classes & Counts ---")
    total_orig = 0
    for c, cnt in orig_counts.items():
        print(f"  • {c:25s} : {cnt:5d} images")
        total_orig += cnt
    print(f"  -> Total in Original Dataset: {total_orig} images")
    
    print("\n--- Detected Augmented Dataset Classes & Counts ---")
    total_aug = 0
    for c, cnt in aug_counts.items():
        print(f"  • {c:25s} : {cnt:5d} images")
        total_aug += cnt
    print(f"  -> Total in Augmented Dataset: {total_aug} images")

    # Combine into DataFrame
    all_classes = sorted(list(set(list(orig_counts.keys()) + list(aug_counts.keys()))))
    rows = []
    for c in all_classes:
        canonical = canonical_mapping.get(c, c)
        rows.append({
            "Folder_Class_Name": c,
            "Normalized_Class_Name": canonical,
            "Original_Dataset_Count": orig_counts.get(c, 0),
            "Augmented_Dataset_Count": aug_counts.get(c, 0)
        })
    df = pd.DataFrame(rows)
    
    # Ensure directories exist
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # Save CSV Report
    report_csv = report_dir / "dataset_class_counts.csv"
    df.to_csv(report_csv, index=False)
    print(f"\n[REPORT SAVED] Class counts saved to: {report_csv}")
    
    # Aggregated canonical summary
    canonical_df = df.groupby("Normalized_Class_Name")[["Original_Dataset_Count", "Augmented_Dataset_Count"]].sum().reset_index()
    canonical_df["Total"] = canonical_df["Original_Dataset_Count"] + canonical_df["Augmented_Dataset_Count"]
    canonical_csv = report_dir / "canonical_class_counts.csv"
    canonical_df.to_csv(canonical_csv, index=False)
    print(f"[REPORT SAVED] Normalized canonical summary saved to: {canonical_csv}")

    # Generate Professional Bar Chart
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = range(len(canonical_df))
    width = 0.38
    
    rects1 = ax.bar([i - width/2 for i in x], canonical_df["Original_Dataset_Count"], width, label="Original Dataset Folder", color="#2b5c8f")
    rects2 = ax.bar([i + width/2 for i in x], canonical_df["Augmented_Dataset_Count"], width, label="Augmented Dataset Folder", color="#e27c38")
    
    ax.set_ylabel("Number of Images", fontsize=12, fontweight="bold")
    ax.set_title("Cotton Leaf Disease Dataset - Raw Image Counts per Class", fontsize=14, fontweight="bold", pad=15)
    ax.set_xticks(list(x))
    ax.set_xticklabels(canonical_df["Normalized_Class_Name"], rotation=30, ha="right", fontsize=10)
    ax.legend(fontsize=11)
    
    # Add values on top of bars
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            if height > 0:
                ax.annotate(f"{height}",
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha="center", va="bottom", fontsize=8)

    autolabel(rects1)
    autolabel(rects2)
    
    plt.tight_layout()
    chart_path = output_dir / "class_distribution.png"
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"[PLOT SAVED] Class distribution chart saved to: {chart_path}")
    print("=" * 70)

if __name__ == "__main__":
    # Project root assumes execution from phase1_cotton/ or parent
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    workspace_root = project_root.parent
    
    # Try finding the Cotton folder
    cotton_root = workspace_root / "Cotton"
    if not cotton_root.exists():
        cotton_root = project_root / "Cotton"
        
    out_dir = project_root / "outputs"
    rep_dir = project_root / "reports"
    
    inspect_dataset(cotton_root, out_dir, rep_dir)
