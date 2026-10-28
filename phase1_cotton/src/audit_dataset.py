"""
Cotton Disease Detection - Phase 1: Comprehensive Dataset Audit
File: src/audit_dataset.py

Objective:
- Audit image files for readability, corruptions, channels, and dimensions.
- Detect exact cryptographic (MD5) duplicates within and across classes.
- Detect OS-specific junk files (e.g. .DS_Store).
- Generate a sample visual grid showing typical leaves from every class.
- Save structured audit metrics to reports/ and outputs/.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from collections import defaultdict, Counter
from PIL import Image, ImageOps
import pandas as pd
import matplotlib.pyplot as plt

def compute_file_md5(file_path: Path, chunk_size=65536) -> str:
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def audit_dataset(data_root: Path, output_dir: Path, report_dir: Path):
    print("=" * 70)
    print("PHASE 1: IMAGE DATASET AUDIT & INTEGRITY CHECK")
    print("=" * 70)
    print(f"Auditing root: {data_root.resolve()}")
    
    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}
    
    audit_results = {
        "total_files_scanned": 0,
        "valid_images": 0,
        "corrupted_images": 0,
        "os_junk_files": 0,
        "class_counts": {},
        "resolutions": Counter(),
        "channels": Counter(),
        "duplicate_hash_count": 0,
    }
    
    hash_to_files = defaultdict(list)
    corrupted_list = []
    os_junk_list = []
    class_sample_images = {}
    
    # We inspect both Original and Augmented directories
    target_dirs = [data_root / "Original Dataset", data_root / "Augmented Dataset"]
    
    for base_dir in target_dirs:
        if not base_dir.exists():
            continue
        print(f"\nScanning: {base_dir.name}...")
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                audit_results["total_files_scanned"] += 1
                fpath = Path(root) / file
                
                # Check for OS junk
                if file.startswith(".") or file in {"Thumbs.db", "desktop.ini"}:
                    audit_results["os_junk_files"] += 1
                    os_junk_list.append(str(fpath.relative_to(data_root)))
                    continue
                
                # Check file extension
                if fpath.suffix.lower() not in valid_extensions:
                    print(f"[UNKNOWN EXT] {fpath}")
                    continue
                
                cls_name = fpath.parent.name
                audit_results["class_counts"][cls_name] = audit_results["class_counts"].get(cls_name, 0) + 1
                
                # Image verification
                try:
                    with Image.open(fpath) as img:
                        img.verify() # Check structural integrity
                    
                    # Reopen to read metadata (verify closes image)
                    with Image.open(fpath) as img:
                        audit_results["resolutions"][img.size] += 1
                        audit_results["channels"][img.mode] += 1
                        audit_results["valid_images"] += 1
                        
                        # Store one sample image per unique class for visual grid
                        if cls_name not in class_sample_images:
                            class_sample_images[cls_name] = fpath
                            
                    # Calculate MD5 hash for exact duplicate detection
                    file_hash = compute_file_md5(fpath)
                    hash_to_files[file_hash].append((str(fpath.relative_to(data_root)), cls_name))
                    
                except Exception as e:
                    audit_results["corrupted_images"] += 1
                    corrupted_list.append({"file": str(fpath.relative_to(data_root)), "error": str(e)})

    # Duplicate analysis
    duplicate_groups = {h: flist for h, flist in hash_to_files.items() if len(flist) > 1}
    audit_results["duplicate_hash_count"] = len(duplicate_groups)
    total_duplicate_instances = sum(len(flist) for flist in duplicate_groups.values())
    
    # Check cross-class label conflicts (identical image labeled as multiple diseases)
    cross_class_conflicts = []
    duplicate_rows = []
    
    for h, flist in duplicate_groups.items():
        classes_in_group = set(cls for _, cls in flist)
        if len(classes_in_group) > 1:
            cross_class_conflicts.append({
                "hash": h,
                "classes": list(classes_in_group),
                "instances": [f for f, _ in flist]
            })
        for f, cls in flist:
            duplicate_rows.append({"hash": h, "file_path": f, "class": cls, "group_size": len(flist)})

    print("\n--- Audit Summary ---")
    print(f"Total Files Scanned      : {audit_results['total_files_scanned']}")
    print(f"Valid Readable Images    : {audit_results['valid_images']}")
    print(f"Corrupt / Unreadable     : {audit_results['corrupted_images']}")
    print(f"OS Junk (.DS_Store etc.) : {audit_results['os_junk_files']}")
    print(f"Unique Image Hashes      : {len(hash_to_files)}")
    print(f"Duplicate Hash Groups    : {len(duplicate_groups)} (Total duplicate files: {total_duplicate_instances})")
    print(f"Cross-Class Label Clashes: {len(cross_class_conflicts)}")
    
    print("\n--- Image Modes / Channels ---")
    for mode, count in audit_results["channels"].items():
        print(f"  Mode {mode}: {count} images")

    print("\n--- Top 5 Image Resolutions ---")
    for res, count in audit_results["resolutions"].most_common(5):
        print(f"  Resolution {res}: {count} images")

    # Export Reports
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # Save duplicates CSV
    if duplicate_rows:
        dup_df = pd.DataFrame(duplicate_rows)
        dup_csv = report_dir / "duplicate_images.csv"
        dup_df.to_csv(dup_csv, index=False)
        print(f"\n[REPORT SAVED] Duplicates log saved to: {dup_csv}")
        
    # Save JSON summary
    summary_export = {
        "total_files": audit_results["total_files_scanned"],
        "valid_images": audit_results["valid_images"],
        "corrupted_images": audit_results["corrupted_images"],
        "os_junk_files": audit_results["os_junk_files"],
        "unique_hashes": len(hash_to_files),
        "duplicate_hash_groups": len(duplicate_groups),
        "cross_class_conflicts_count": len(cross_class_conflicts),
        "cross_class_conflicts": cross_class_conflicts[:10], # sample
        "top_resolutions": [f"{w}x{h}: {c}" for (w, h), c in audit_results["resolutions"].most_common(5)],
        "channels": dict(audit_results["channels"])
    }
    
    json_path = report_dir / "audit_summary.json"
    with open(json_path, "w") as f:
        json.dump(summary_export, f, indent=2)
    print(f"[REPORT SAVED] Audit metrics JSON saved to: {json_path}")

    # Generate Visual Sample Grid
    if class_sample_images:
        classes = sorted(list(class_sample_images.keys()))
        n_classes = len(classes)
        cols = 3
        rows = (n_classes + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(12, 4 * rows))
        axes = axes.flatten()
        
        for idx, cls in enumerate(classes):
            img_path = class_sample_images[cls]
            try:
                with Image.open(img_path) as img:
                    axes[idx].imshow(img)
                    axes[idx].set_title(f"{cls}\n({img.size[0]}x{img.size[1]}, {img.mode})", fontsize=10, fontweight="bold")
                    axes[idx].axis("off")
            except Exception as e:
                axes[idx].text(0.5, 0.5, f"Error: {e}", ha="center", va="center")
                axes[idx].axis("off")
                
        # Turn off unused subplots
        for idx in range(len(classes), len(axes)):
            axes[idx].axis("off")
            
        plt.tight_layout()
        grid_path = output_dir / "dataset_samples.png"
        plt.savefig(grid_path, dpi=200)
        plt.close()
        print(f"[PLOT SAVED] Dataset visual grid saved to: {grid_path}")
    print("=" * 70)

if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    workspace_root = project_root.parent
    cotton_root = workspace_root / "Cotton"
    if not cotton_root.exists():
        cotton_root = project_root / "Cotton"
        
    audit_dataset(cotton_root, project_root / "outputs", project_root / "reports")
