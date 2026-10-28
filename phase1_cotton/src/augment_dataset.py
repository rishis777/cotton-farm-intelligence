"""
Cotton Disease Detection - Phase 1: Scientific Image Augmentation Pipeline
File: src/augment_dataset.py

Objective:
- Implement label-preserving transformations (horizontal flip, +/-15° rotation, brightness, contrast, mild zoom).
- Restrict augmentations strictly to the training partition (preventing evaluation leakage).
- Create an inspection grid demonstrating each transformation on real leaf samples.
- Support class balancing by generating augmentations for minority classes.
- Save documentation and inspection grids to outputs/ and reports/.
"""

import os
import sys
import json
import random
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps
import matplotlib.pyplot as plt

def apply_horizontal_flip(img: Image.Image) -> Image.Image:
    """Realistic horizontal reflection - natural leaf orientation variation."""
    return ImageOps.mirror(img)

def apply_mild_rotation(img: Image.Image, angle: float) -> Image.Image:
    """Small rotation (-15 to +15 degrees) without erasing symptoms."""
    # Rotate with bilinear filtering and expand=False to preserve dimensions
    return img.rotate(angle, resample=Image.BILINEAR, expand=False)

def apply_brightness(img: Image.Image, factor: float) -> Image.Image:
    """Simulates real-world outdoor lighting changes (sunlight vs overcast)."""
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(factor)

def apply_contrast(img: Image.Image, factor: float) -> Image.Image:
    """Simulates camera exposure and shadow contrast variations."""
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(factor)

def apply_conservative_zoom(img: Image.Image, zoom_factor: float) -> Image.Image:
    """Conservative crop (90% to 100%) keeping main leaf lesions intact."""
    w, h = img.size
    crop_w = int(w * zoom_factor)
    crop_h = int(h * zoom_factor)
    left = (w - crop_w) // 2
    top = (h - crop_h) // 2
    cropped = img.crop((left, top, left + crop_w, top + crop_h))
    return cropped.resize((w, h), resample=Image.BILINEAR)

def generate_inspection_grid(train_dir: Path, output_path: Path):
    """
    Generates a visual comparison grid:
    Original | Horizontal Flip | Small Rotation (+12°) | Brightness (1.15) | Contrast (0.85) | Mild Zoom (90%)
    """
    print("\nGenerating visual augmentation inspection grid...")
    classes = sorted([d.name for d in train_dir.iterdir() if d.is_dir()])
    
    transform_names = [
        "Original", 
        "H-Flip\n(Orientation)", 
        "Rotation (+12°)\n(Angle)", 
        "Brightness (1.15x)\n(Lighting)", 
        "Contrast (0.85x)\n(Exposure)", 
        "Zoom (0.92x)\n(Scale)"
    ]
    
    fig, axes = plt.subplots(len(classes), len(transform_names), figsize=(16, 2.8 * len(classes)))
    
    for r_idx, cls in enumerate(classes):
        cls_dir = train_dir / cls
        img_files = [f for f in cls_dir.iterdir() if f.is_file() and not f.name.startswith(".")]
        if not img_files:
            continue
            
        sample_file = img_files[0]
        with Image.open(sample_file) as raw_img:
            img = raw_img.convert("RGB")
            
        variants = [
            img,
            apply_horizontal_flip(img),
            apply_mild_rotation(img, 12.0),
            apply_brightness(img, 1.15),
            apply_contrast(img, 0.85),
            apply_conservative_zoom(img, 0.92)
        ]
        
        for c_idx, var_img in enumerate(variants):
            ax = axes[r_idx, c_idx]
            ax.imshow(var_img)
            if r_idx == 0:
                ax.set_title(transform_names[c_idx], fontsize=11, fontweight="bold", pad=8)
            if c_idx == 0:
                ax.set_ylabel(cls, fontsize=10, fontweight="bold", rotation=0, labelpad=70, va="center")
            ax.set_xticks([])
            ax.set_yticks([])
            
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"[PLOT SAVED] Inspection grid saved to: {output_path}")

def build_augmented_training_set(
    train_dir: Path, 
    dest_dir: Path, 
    target_count_per_class: int = 800, 
    seed: int = 42
):
    """
    Balances the training partition by creating realistic augmented images
    up to target_count_per_class.
    """
    random.seed(seed)
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    classes = sorted([d.name for d in train_dir.iterdir() if d.is_dir()])
    aug_summary = {}
    
    print(f"\nBuilding balanced augmented training set (Target: {target_count_per_class} images/class)...")
    
    for cls in classes:
        cls_src = train_dir / cls
        cls_dst = dest_dir / cls
        cls_dst.mkdir(parents=True, exist_ok=True)
        
        src_files = [f for f in cls_src.iterdir() if f.is_file() and not f.name.startswith(".")]
        initial_count = len(src_files)
        
        # 1. Copy all original train images first
        for f in src_files:
            shutil_dst = cls_dst / f.name
            if not shutil_dst.exists():
                shutil_dst.write_bytes(f.read_bytes())
                
        needed = max(0, target_count_per_class - initial_count)
        generated = 0
        
        # 2. Synthesize augmentations from existing train files
        while generated < needed:
            parent_file = random.choice(src_files)
            try:
                with Image.open(parent_file) as raw_img:
                    img = raw_img.convert("RGB")
                    
                # Apply random pipeline
                if random.random() > 0.5:
                    img = apply_horizontal_flip(img)
                rot_angle = random.uniform(-15.0, 15.0)
                img = apply_mild_rotation(img, rot_angle)
                bright = random.uniform(0.85, 1.15)
                img = apply_brightness(img, bright)
                cont = random.uniform(0.85, 1.15)
                img = apply_contrast(img, cont)
                zoom = random.uniform(0.90, 1.0)
                img = apply_conservative_zoom(img, zoom)
                
                gen_name = f"synth_aug_{generated}_{parent_file.stem}.jpg"
                img.save(cls_dst / gen_name, format="JPEG", quality=92)
                generated += 1
            except Exception as e:
                print(f"[ERROR] Failed augmenting {parent_file}: {e}")
                break
                
        final_count = initial_count + generated
        aug_summary[cls] = {
            "initial_train_count": initial_count,
            "synthesized_augmented": generated,
            "final_balanced_train_count": final_count
        }
        print(f"  • {cls:20s}: {initial_count:4d} initial + {generated:4d} augmented -> {final_count:4d} total")
        
    return aug_summary

if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    train_dir = project_root / "data" / "split" / "train"
    aug_train_dir = project_root / "data" / "augmented_train"
    out_grid = project_root / "outputs" / "augmentation_inspection_grid.png"
    rep_summary = project_root / "reports" / "augmentation_summary.json"
    
    if not train_dir.exists():
        print(f"[ERROR] Split training directory not found at: {train_dir}")
        print("Please run 'src/split_dataset.py' first.")
        sys.exit(1)
        
    generate_inspection_grid(train_dir, out_grid)
    summary = build_augmented_training_set(train_dir, aug_train_dir, target_count_per_class=800, seed=42)
    
    with open(rep_summary, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[REPORT SAVED] Augmentation summary saved to: {rep_summary}")
    print("=" * 70)
