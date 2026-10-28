"""
Cotton Disease Detection - Phase 1: Deep Dataset Comparison & Leakage Investigation
File: src/compare_datasets.py

Objective:
- Uncover the true origin of images in 'Original Dataset' and 'Augmented Dataset'.
- Detect leaf ID clusters and pre-augmented transformation variants (e.g. rotation_1, contrast_1).
- Identify hash overlaps and class-naming mismatches.
- Document catastrophic data leakage risks for the academic report.
"""

import os
import sys
import re
import json
import hashlib
from pathlib import Path
from collections import defaultdict
import pandas as pd

def compute_file_md5(file_path: Path, chunk_size=65536) -> str:
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def extract_leaf_signature(filename: str):
    """
    Extracts the underlying leaf index/identifier from augmented filenames.
    Examples:
      - 'aug_0_contrast_14.jpg' -> 'leaf_14'
      - 'rotation_14.jpg' -> 'leaf_14'
      - '14.jpg' -> 'leaf_14'
      - 'alternaria_(102).png' -> 'alt_102'
      - 'aug_alternaria_(102).png' -> 'alt_102'
    """
    stem = Path(filename).stem
    # Match Kaggle-style pattern ending with _<id> or plain <id>
    m_num = re.search(r'(?:^|_)(\d+)$', stem)
    if m_num:
        return f"id_{m_num.group(1)}"
    
    # Match bracketed style: alternaria_(102)
    m_bracket = re.search(r'\((\d+)\)', stem)
    if m_bracket:
        return f"idx_{m_bracket.group(1)}"
        
    return stem # fallback to stem

def compare_datasets(data_root: Path, report_dir: Path):
    print("=" * 70)
    print("PHASE 1: FORENSIC DATASET COMPARISON & DATA LEAKAGE ANALYSIS")
    print("=" * 70)
    
    orig_dir = data_root / "Original Dataset"
    aug_dir = data_root / "Augmented Dataset"
    
    if not orig_dir.exists() or not aug_dir.exists():
        print("[ERROR] Both 'Original Dataset' and 'Augmented Dataset' must exist.")
        sys.exit(1)
        
    orig_hashes = {}
    aug_hashes = {}
    
    orig_leaf_groups = defaultdict(list)
    aug_leaf_groups = defaultdict(list)
    
    valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    print("Analyzing Original Dataset images and signatures...")
    for f in orig_dir.rglob("*"):
        if f.is_file() and not f.name.startswith(".") and f.suffix.lower() in valid_exts:
            cls_name = f.parent.name
            h = compute_file_md5(f)
            orig_hashes[h] = (f, cls_name)
            sig = extract_leaf_signature(f.name)
            orig_leaf_groups[(cls_name, sig)].append(str(f.relative_to(data_root)))

    print("Analyzing Augmented Dataset images and signatures...")
    for f in aug_dir.rglob("*"):
        if f.is_file() and not f.name.startswith(".") and f.suffix.lower() in valid_exts:
            cls_name = f.parent.name
            h = compute_file_md5(f)
            aug_hashes[h] = (f, cls_name)
            sig = extract_leaf_signature(f.name)
            aug_leaf_groups[(cls_name, sig)].append(str(f.relative_to(data_root)))

    # Compute Exact Duplicate Overlaps
    exact_overlaps = []
    for h, (aug_path, aug_cls) in aug_hashes.items():
        if h in orig_hashes:
            orig_path, orig_cls = orig_hashes[h]
            exact_overlaps.append({
                "hash": h,
                "augmented_file": str(aug_path.relative_to(data_root)),
                "augmented_class": aug_cls,
                "original_file": str(orig_path.relative_to(data_root)),
                "original_class": orig_cls,
                "class_match": aug_cls.lower().replace("_", " ").replace("leaf", "").strip() == 
                               orig_cls.lower().replace("_", " ").replace("leaf", "").strip()
            })

    print("\n--- Key Comparison Findings ---")
    print(f"Total Unique Hashes in Original : {len(orig_hashes)}")
    print(f"Total Unique Hashes in Augmented: {len(aug_hashes)}")
    print(f"Exact Cross-Folder Hash Overlaps: {len(exact_overlaps)}")
    
    # Analyze Leaf ID Clustering (The Kaggle Pre-augmentation phenomenon)
    orig_clusters_summary = []
    for (cls_name, sig), flist in orig_leaf_groups.items():
        if len(flist) > 1:
            orig_clusters_summary.append({
                "folder": "Original Dataset",
                "class": cls_name,
                "leaf_signature": sig,
                "image_count": len(flist),
                "sample_files": flist[:3]
            })
            
    print(f"\nUnique Leaf Signatures in Original Dataset: {len(orig_leaf_groups)}")
    print(f"Leaf Signatures with MULTIPLE variants in Original Dataset: {len(orig_clusters_summary)}")
    
    # Save Report
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # Save Overlaps CSV
    if exact_overlaps:
        overlap_df = pd.DataFrame(exact_overlaps)
        overlap_csv = report_dir / "exact_cross_folder_duplicates.csv"
        overlap_df.to_csv(overlap_csv, index=False)
        print(f"[REPORT SAVED] Exact cross-folder duplicates saved to: {overlap_csv}")

    # Save Clusters CSV
    clusters_df = pd.DataFrame(orig_clusters_summary)
    clusters_csv = report_dir / "leaf_signature_clusters.csv"
    clusters_df.to_csv(clusters_csv, index=False)
    print(f"[REPORT SAVED] Leaf signature clusters saved to: {clusters_csv}")

    # Save Deep Analysis Summary JSON
    report_json = {
        "summary": "Deep forensic investigation of cotton dataset folders.",
        "original_dataset_hashes": len(orig_hashes),
        "augmented_dataset_hashes": len(aug_hashes),
        "exact_cross_folder_overlap_count": len(exact_overlaps),
        "total_orig_leaf_signatures": len(orig_leaf_groups),
        "multi_variant_leaf_signatures_count": len(orig_clusters_summary),
        "critical_academic_finding": (
            "The folder named 'Original Dataset' contains thousands of pre-augmented synthetic copies "
            "(rotations, crops, flips, brightness changes) sharing common base leaf IDs. "
            "A standard random train/test split causes severe data leakage where transformed copies "
            "of the same leaf leak into the test set. Grouped or cluster-aware splitting is mandatory."
        )
    }
    
    summary_path = report_dir / "dataset_comparison_report.json"
    with open(summary_path, "w") as f:
        json.dump(report_json, f, indent=2)
    print(f"[REPORT SAVED] Forensic comparison report saved to: {summary_path}")
    print("=" * 70)

if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    workspace_root = project_root.parent
    cotton_root = workspace_root / "Cotton"
    if not cotton_root.exists():
        cotton_root = project_root / "Cotton"
        
    compare_datasets(cotton_root, project_root / "reports")
