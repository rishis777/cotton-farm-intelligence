# Cotton Disease Detection and Image Augmentation (Phase 1)
### Target Context: Cotton Cultivation in Dhule District, Khandesh Region, Maharashtra, India

---

## 1. Problem Statement
Cotton (*Gossypium hirsutum*) is a vital cash crop in Maharashtra, particularly across the Khandesh agro-climatic belt (Dhule, Jalgaon, and Nandurbar districts). However, cotton yields suffer drastic reductions due to foliar diseases (Alternaria leaf spot, Bacterial blight, Powdery mildew, Target spot, Fusarium and Verticillium wilts) and pest infestations (Aphids, Army worm). 

Smallholder farmers in Dhule often lack immediate access to plant pathologists, leading to delayed or inaccurate chemical applications. Automating foliar disease diagnosis using Computer Vision and Transfer Learning provides a rapid, accessible screening mechanism. However, publicly available cotton datasets suffer from severe data leakage, duplicated images, and uncalibrated augmentations. 

Phase 1 establishes a scientifically sound, leakage-proof, and reproducible deep learning baseline using MobileNetV2, setting the rigorous benchmark for future regional field trials in Dhule.

---

## 2. Phase 1 Objectives & Scope
- **Dataset Audit & Discovery**: Mathematically verify actual image counts, corruptions, duplicate hashes, and folder naming discrepancies in online-sourced datasets.
- **Forensic Data Leakage Prevention**: Identify pre-augmented image clusters (e.g. rotation/contrast copies sharing underlying leaf IDs) and isolate them using Disjoint Set Union (DSU) cluster splitting to prevent evaluation leakage.
- **Label-Preserving Augmentation**: Construct an augmentation pipeline restricted strictly to the training partition (horizontal flips, mild ±15° rotation, lighting/contrast jitter).
- **Transfer Learning Baseline**: Train MobileNetV2 with ImageNet pretrained weights, frozen backbone, dropout regularized classifier, and balanced class weighting.
- **Rigorous Evaluation & Error Analysis**: Evaluate on an untouched, unaugmented test set reporting Macro-F1, Weighted-F1, Confusion Matrix, and per-class precision/recall.
- **Inference CLI**: Deliver an end-to-end command-line prediction script with Top-3 probabilities and academic field disclaimers.

> **Regional Disclaimer**: Phase 1 is trained and evaluated on online benchmark datasets. While designed for future Dhule application, field validation requires independent on-site leaf image collection in Dhule farms.

---

## 3. Dataset Classes & Actual Statistics

From forensic inspection of the 14,955 raw files across `Original Dataset` and `Augmented Dataset`, the 9 canonical classes and distribution are:

| Canonical Disease / Pest Class | Original Folder Name | Total Verified Images | Unique Leaf Clusters |
| :--- | :--- | :---: | :---: |
| **Alternaria Leaf** | `Alternaria Leaf Spot` / `Alternaria_Leaf` | 1,143 | 986 |
| **Aphids** | `Aphids` | 1,560 | 150 |
| **Army Worm** | `Army_worm` | 1,575 | 151 |
| **Bacterial Blight** | `Bacterial_Blight` | 2,465 | 1,170 |
| **Fusarium Wilt** | `Fusarium Wilt` / `Fusarium_Wilt` | 1,294 | 957 |
| **Healthy Leaf** | `Healthy` / `Healthy_Leaf` | 2,455 | 1,160 |
| **Powdery Mildew** | `Powdery_Mildew` | 1,579 | 151 |
| **Target Spot** | `Target_spot` | 1,561 | 150 |
| **Verticillium Wilt** | `Verticillium Wilt` / `Verticillium_Wilt` | 1,291 | 977 |
| **Total** | — | **14,923** | **5,852** |

*Note: 14 image files with identical hashes labeled across multiple conflicting classes and 4 macOS metadata files (.DS_Store) were automatically detected and purged.*

---

## 4. Methodology & Leakage Prevention Protocol

### The Data Leakage Discovery
In standard online cotton datasets, minority classes were pre-augmented by the original uploaders using transformations like `contrast_14.jpg`, `rotation_14.jpg`, and `crop_14.jpg`. A naive random train/test split leaks transformed copies of the same leaf into the test set, creating artificially inflated (~99.9%) test accuracy.

### Our Solution: Connected Cluster Splitting
1. **Signature & Hash Union**: Images sharing common base IDs or identical cryptographic MD5 hashes are grouped into unified clusters using Disjoint Set Union (DSU).
2. **Cluster-Level Partitioning**: All images in a cluster are assigned exclusively to Train (~70%), Validation (~15%), or Test (~15%).
3. **Clean Evaluation Guarantee**: Test and validation sets contain strictly unaugmented, clean leaf images.

---

## 5. Model Architecture & Training Protocol

- **Backbone**: MobileNetV2 (ImageNet weights, frozen feature extractor, 1,280 features).
- **Classification Head**: `Dropout(p=0.3) -> Linear(1280, 9)`.
- **Input Dimensions**: 224 x 224 x 3.
- **Normalization**: ImageNet standards (`mean=[0.485, 0.456, 0.406]`, `std=[0.229, 0.224, 0.225]`).
- **Loss Function**: Weighted Cross-Entropy Loss (balanced class weights).
- **Optimizer**: Adam (`lr=0.001`).
- **Reproducibility**: Random Seed = 42 across NumPy, PyTorch, and Python.

---

## 6. Directory Structure
```
phase1_cotton/
├── data/
│   ├── split/
│   │   ├── train/
│   │   ├── validation/
│   │   └── test/
│   └── augmented_train/
├── models/
│   ├── best_cotton_mobilenetv2.pt
│   └── class_mapping.json
├── outputs/
│   ├── class_distribution.png
│   ├── dataset_samples.png
│   ├── split_distribution.png
│   ├── augmentation_inspection_grid.png
│   ├── training_curves.png
│   ├── confusion_matrix.png
│   └── class_wise_metrics.png
├── reports/
│   ├── dataset_class_counts.csv
│   ├── canonical_class_counts.csv
│   ├── audit_summary.json
│   ├── duplicate_images.csv
│   ├── exact_cross_folder_duplicates.csv
│   ├── leaf_signature_clusters.csv
│   ├── dataset_manifest.csv
│   ├── split_summary.csv
│   ├── training_history.json
│   ├── evaluation_results.json
│   └── misclassified_test_images.csv
├── src/
│   ├── inspect_dataset.py
│   ├── audit_dataset.py
│   ├── compare_datasets.py
│   ├── split_dataset.py
│   ├── augment_dataset.py
│   ├── train_model.py
│   ├── evaluate_model.py
│   └── predict_image.py
├── tests/
│   └── test_pipeline.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 7. Execution Guide (Step by Step)

### 1. Environment Setup
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Dataset Inspection & Audit
```powershell
python src/inspect_dataset.py
python src/audit_dataset.py
python src/compare_datasets.py
```

### 3. Leakage-Safe Splitting & Augmentation
```powershell
python src/split_dataset.py
python src/augment_dataset.py
```

### 4. Run Test Suite
```powershell
pytest tests/test_pipeline.py -v
```

### 5. Model Training & Evaluation
```powershell
python src/train_model.py
python src/evaluate_model.py
```

### 6. Predict on New Cotton Leaf Image
```powershell
python src/predict_image.py --image "data/split/test/Alternaria_Leaf/<sample_image.png>"
```

---

### 7. Evaluation Results (Untouched Test Set)
Evaluated on **871 clean, unseen test images** across all 9 classes:
- **Test Accuracy**: **89.90%**
- **Macro F1-Score**: **0.8741**
- **Weighted F1-Score**: **0.8966**
- **Macro Precision**: **0.8660**
- **Macro Recall**: **0.8905**
- **Data Leakage Check**: **0 identical images between Train and Test ($|Train \cap Test| = 0$)**

---

## 8. Academic Deliverables & Limitations

### Known Limitations
1. **Domain Gap**: Dataset images were captured under controlled or varied laboratory/online conditions. Real Dhule fields present severe background clutter, dust, insect damage, and multiple co-occurring diseases.
2. **MobileNetV2 Baseline vs Few-Shot Learning**: This baseline evaluates standard transfer learning. Genuine Few-Shot Learning (e.g. Prototypical Networks, Relation Networks) requires episode-based meta-learning with N-way K-shot evaluation protocols.
3. **Probability Calibration**: Softmax output values reflect relative model confidence, not true Bayesian posterior probabilities.
