"""
Cotton Disease Detection - Phase 1: Leakage-Safe Stratified Group Splitting
File: src/split_dataset.py

Objective:
- Prevent catastrophic data leakage caused by:
  1. Pre-augmented variants sharing leaf IDs.
  2. Exact duplicate images having different filenames (e.g. fusarium_(10) and fusarium_(11)).
- Connect images via Disjoint Set Union (by both leaf signature and hash) into strictly isolated clusters.
- Split clusters: ~70% Train, ~15% Validation, ~15% Test with fixed random seed (42).
- Populate 'data/split/train', 'data/split/validation', 'data/split/test'.
- Keep validation and test partitions unaugmented / clean.
- Save complete manifest to 'reports/dataset_manifest.csv'.
"""

import os
import sys
import re
import json
import shutil
import hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def compute_file_md5(file_path: Path, chunk_size=65536) -> str:
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def extract_leaf_signature(filename: str) -> str:
    stem = Path(filename).stem
    m_num = re.search(r'(?:^|_)(\d+)$', stem)
    if m_num:
        return f"id_{m_num.group(1)}"
    m_bracket = re.search(r'\((\d+)\)', stem)
    if m_bracket:
        return f"idx_{m_bracket.group(1)}"
    return stem

def is_clean_base_image(filename: str) -> bool:
    name_lower = filename.lower()
    aug_keywords = ["aug", "flip", "rotation", "contrast", "constract", "zoom", "crop", "translation", "pil", "rotozoom"]
    for kw in aug_keywords:
        if kw in name_lower:
            return False
    return True

# Disjoint Set Union (Union-Find) to merge clusters by signature AND by identical hash
class DisjointSet:
    def __init__(self):
        self.parent = {}
    def find(self, i):
        if i not in self.parent:
            self.parent[i] = i
            return i
        if self.parent[i] != i:
            self.parent[i] = self.find(self.parent[i])
        return self.parent[i]
    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            self.parent[root_i] = root_j

def split_dataset(data_root: Path, project_root: Path, seed: int = 42):
    print("=" * 70)
    print("PHASE 1: LEAKAGE-SAFE DATASET SPLITTING (CONNECTED CLUSTER SPLIT)")
    print("=" * 70)
    
    np.random.seed(seed)
    
    canonical_mapping = {
        "alternaria leaf spot": "Alternaria_Leaf",
        "alternaria_leaf": "Alternaria_Leaf",
        "aphids": "Aphids",
        "army_worm": "Army_worm",
        "bacterial_blight": "Bacterial_Blight",
        "fusarium wilt": "Fusarium_Wilt",
        "fusarium_wilt": "Fusarium_Wilt",
        "healthy": "Healthy_Leaf",
        "healthy_leaf": "Healthy_Leaf",
        "powdery_mildew": "Powdery_Mildew",
        "target_spot": "Target_spot",
        "verticillium wilt": "Verticillium_Wilt",
        "verticillium_wilt": "Verticillium_Wilt",
    }
    
    valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    
    print("Step 1: Indexing all dataset files and calculating hashes...")
    hash_to_classes = defaultdict(set)
    all_files_info = []
    
    for sub in ["Original Dataset", "Augmented Dataset"]:
        sub_dir = data_root / sub
        if not sub_dir.exists():
            continue
        for f in sub_dir.rglob("*"):
            if f.is_file() and not f.name.startswith(".") and f.suffix.lower() in valid_exts:
                raw_cls = f.parent.name
                norm_cls = canonical_mapping.get(raw_cls.lower().strip(), raw_cls)
                h = compute_file_md5(f)
                hash_to_classes[h].add(norm_cls)
                all_files_info.append({
                    "path": f,
                    "folder": sub,
                    "raw_class": raw_cls,
                    "class": norm_cls,
                    "filename": f.name,
                    "hash": h,
                    "signature": extract_leaf_signature(f.name),
                    "is_clean": is_clean_base_image(f.name)
                })

    conflicted_hashes = {h for h, clist in hash_to_classes.items() if len(clist) > 1}
    print(f"Detected {len(conflicted_hashes)} hashes with cross-class label conflicts (dropping to ensure purity).")
    
    filtered_images = [img for img in all_files_info if img["hash"] not in conflicted_hashes]
    print(f"Total valid unconflicted images for splitting: {len(filtered_images)}")

    # Step 2: Unify clusters using Disjoint Set Union (DSU) per class
    # Two images are united if they have the same signature OR the same hash
    print("\nStep 2: Unifying clusters via Signature & Hash Connected Components...")
    class_dsu = defaultdict(DisjointSet)
    class_images = defaultdict(list)
    
    for img in filtered_images:
        cls = img["class"]
        class_images[cls].append(img)
        dsu = class_dsu[cls]
        
        sig_node = f"sig_{img['signature']}"
        hash_node = f"hash_{img['hash']}"
        dsu.union(sig_node, hash_node)

    # Group images by their canonical cluster root
    class_clusters = defaultdict(lambda: defaultdict(list))
    for cls, img_list in class_images.items():
        dsu = class_dsu[cls]
        for img in img_list:
            sig_node = f"sig_{img['signature']}"
            cluster_id = dsu.find(sig_node)
            img["cluster_id"] = cluster_id
            class_clusters[cls][cluster_id].append(img)

    for cls in sorted(class_clusters.keys()):
        clusters = class_clusters[cls]
        total_imgs = sum(len(imgs) for imgs in clusters.values())
        print(f"  • {cls:20s}: {len(clusters):4d} connected clusters ({total_imgs:5d} images)")

    # Step 3: Stratified Cluster Split (~70% train, ~15% val, ~15% test)
    split_records = []
    print("\nStep 3: Performing leakage-safe cluster allocation...")
    for cls in sorted(class_clusters.keys()):
        clusters = list(class_clusters[cls].keys())
        np.random.shuffle(clusters)
        
        n_clusters = len(clusters)
        n_val = max(1, int(round(0.15 * n_clusters)))
        n_test = max(1, int(round(0.15 * n_clusters)))
        n_train = n_clusters - n_val - n_test
        if n_train < 1:
            n_train = max(1, n_clusters - 2)
            n_val = 1
            n_test = max(1, n_clusters - n_train - n_val)
            
        train_clusters = set(clusters[:n_train])
        val_clusters = set(clusters[n_train:n_train + n_val])
        test_clusters = set(clusters[n_train + n_val:])
        
        for c_id, img_list in class_clusters[cls].items():
            if c_id in train_clusters:
                target_split = "train"
                for img in img_list:
                    split_records.append({**img, "split": target_split})
            elif c_id in val_clusters:
                target_split = "validation"
                clean_imgs = [img for img in img_list if img["is_clean"]]
                selected = clean_imgs if clean_imgs else [img_list[0]]
                for img in selected:
                    split_records.append({**img, "split": target_split})
            else:
                target_split = "test"
                clean_imgs = [img for img in img_list if img["is_clean"]]
                selected = clean_imgs if clean_imgs else [img_list[0]]
                for img in selected:
                    split_records.append({**img, "split": target_split})

    df_manifest = pd.DataFrame(split_records)
    
    # Step 4: Copy images to physical split directory
    split_dir = project_root / "data" / "split"
    for s in ["train", "validation", "test"]:
        s_path = split_dir / s
        if s_path.exists():
            shutil.rmtree(s_path)
        s_path.mkdir(parents=True, exist_ok=True)
        for cls in sorted(class_clusters.keys()):
            (s_path / cls).mkdir(parents=True, exist_ok=True)

    print("\nStep 4: Copying images into 'data/split/' directories...")
    dest_counts = defaultdict(int)
    for idx, row in df_manifest.iterrows():
        src_path = row["path"]
        cls = row["class"]
        split = row["split"]
        
        dest_filename = f"{row['signature']}_{row['filename']}"
        dest_counts[dest_filename] += 1
        if dest_counts[dest_filename] > 1:
            dest_filename = f"{dest_counts[dest_filename]}_{dest_filename}"
            
        dest_path = split_dir / split / cls / dest_filename
        shutil.copy2(src_path, dest_path)
        df_manifest.at[idx, "dest_path"] = str(dest_path.relative_to(project_root))

    # Step 5: Manifest & Summaries
    report_dir = project_root / "reports"
    output_dir = project_root / "outputs"
    report_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    manifest_csv = report_dir / "dataset_manifest.csv"
    export_df = df_manifest[["split", "class", "filename", "signature", "cluster_id", "is_clean", "hash", "dest_path"]]
    export_df.to_csv(manifest_csv, index=False)
    print(f"\n[MANIFEST SAVED] Dataset manifest saved to: {manifest_csv}")

    split_summary = df_manifest.groupby(["class", "split"]).size().unstack(fill_value=0)
    for col in ["train", "validation", "test"]:
        if col not in split_summary.columns:
            split_summary[col] = 0
    split_summary["total"] = split_summary["train"] + split_summary["validation"] + split_summary["test"]
    
    split_csv = report_dir / "split_summary.csv"
    split_summary.to_csv(split_csv)
    print(f"[REPORT SAVED] Split summary saved to: {split_csv}")
    
    print("\n--- Final Leakage-Safe Split Counts ---")
    print(split_summary)

    # Plot Split Distribution
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    ax = split_summary[["train", "validation", "test"]].plot(
        kind="bar", stacked=True, figsize=(12, 6), color=["#2b5c8f", "#f2a900", "#38b000"]
    )
    plt.title("Leakage-Safe Dataset Partition (Train / Val / Test by Connected Cluster)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Disease Class", fontsize=11, fontweight="bold")
    plt.ylabel("Number of Partitioned Images", fontsize=11, fontweight="bold")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plot_path = output_dir / "split_distribution.png"
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"[PLOT SAVED] Split distribution chart saved to: {plot_path}")
    print("=" * 70)

if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    workspace_root = project_root.parent
    cotton_root = workspace_root / "Cotton"
    if not cotton_root.exists():
        cotton_root = project_root / "Cotton"
        
    split_dataset(cotton_root, project_root, seed=42)
