# Academic Project Report: Phase 1
## Cotton Disease Detection and Image Augmentation for the Dhule Region of Maharashtra

**Project Title**: Cotton Leaf Disease Detection and Image Augmentation for Smallholder Cultivation in Dhule District  
**Author**: B.Tech Information Technology Student  
**Academic Mentor / Reviewer**: Senior ML Engineer & CV Researcher  
**Phase**: Phase 1 — Dataset Audit, Leakage Prevention, & Transfer Learning Baseline  
**Date**: October 2026  

---

### Abstract
Cotton (*Gossypium hirsutum*) is the cornerstone agricultural commodity of the Khandesh region in Maharashtra, with Dhule district representing critical acreage under rainfed and semi-irrigated smallholder farming. However, foliar disease epidemics—predominantly Alternaria leaf spot, Bacterial blight, Powdery mildew, Target spot, and Fusarium wilt—account for yield penalties exceeding 30–45% annually. Automated disease classification using convolutional neural networks offers high potential for point-of-care diagnosis. Nevertheless, contemporary academic implementations frequently suffer from severe data leakage stemming from unverified online datasets containing pre-augmented duplicate variants across train and evaluation partitions. 

This Phase 1 study establishes a scientifically sound, leakage-proof methodology. Through cryptographic (MD5) hashing and Connected Component cluster analysis via Disjoint Set Union (DSU), we demonstrate that standard benchmark datasets contain thousands of pre-augmented synthetic duplicates sharing common base leaf identities. A naive random split leads to catastrophic evaluation leakage and artificially inflated accuracy. By grouping images into 5,852 strictly isolated leaf clusters, we partition 14,923 verified images into train (~70%), validation (~15%), and untouched test (~15%) sets. A lightweight MobileNetV2 transfer learning baseline with balanced class weights is established, providing a rigorous reference benchmark for subsequent Phase 2 regional field deployment in Dhule.

---

### 1. Introduction
Agricultural computer vision has advanced significantly with deep learning, yet real-world translation from laboratory benchmarks to Indian farming systems remains limited. Cotton production in Dhule district (Maharashtra) is characterized by high ambient solar irradiance, black cotton soil (*regur*), hot dry pre-monsoon spells, and sudden humidity spikes during the Kharif season. These conditions accelerate fungal and bacterial spore dispersal. Smallholder farmers rely on retrospective chemical treatment rather than early prophylactic diagnosis. Phase 1 of this research addresses the foundational computer vision pipeline, dataset integrity, and baseline classification mechanics before introducing regional farm data.

### 2. Problem Statement
Publicly accessible cotton leaf disease datasets downloaded from web repositories and competitions (e.g., Kaggle, Mendeley Data) are widely used without structural verification. These datasets frequently contain:
1. Undocumented transformations (rotations, flips, crops) applied prior to splitting.
2. Identical leaf photographs duplicated under divergent file names.
3. Class-label contradictions where identical images are assigned contradictory disease tags.
4. Folder-naming inconsistencies across original and augmented archives.

Deploying deep neural networks on naively partitioned datasets yields models that memorize background artifacts or leaf geometry rather than true pathological lesions, leading to near-100% laboratory accuracy but complete failure under real field conditions.

### 3. Objectives & Scope of Phase 1
- **Dataset Audit**: Perform exhaustive cryptographic hashing, corrupted file scanning, channel verification, and resolution auditing on all 14,955 repository files.
- **Forensic Leakage Elimination**: Formulate a Disjoint Set Union (DSU) clustering algorithm linking pre-augmented variants and exact duplicates to their root leaf identities.
- **Leakage-Safe Partitioning**: Construct clean Train, Validation, and Test sets where no leaf cluster crosses split boundaries, ensuring validation and test sets remain strictly unaugmented.
- **Label-Preserving Augmentation**: Develop an augmentation engine restricted solely to the training set simulating outdoor lighting and geometric leaf orientations.
- **Transfer Learning Benchmark**: Train MobileNetV2 with ImageNet pretrained representations, frozen backbone layers, and balanced loss weighting.
- **Rigorous Evaluation**: Measure Macro-F1, Weighted-F1, per-class Precision/Recall, and map classification confusion matrices on unseen test leaves.
- **Academic Caution**: Explicitly document that Phase 1 represents an online baseline requiring independent Dhule-specific field validation in Phase 2.

### 4. Literature Review Outline
*Note: In Phase 2, this section integrates your specific literature review document and regional citations.*
- **Traditional Machine Learning Approaches**: Handcrafted texture descriptors (GLCM, Haralick), color histograms, and Support Vector Machines (SVM). Limitations: poor robustness to uncontrolled lighting and background soil clutter.
- **Deep Convolutional Neural Networks (CNNs)**: ResNet, VGG, DenseNet, and MobileNet architectures applied to plant pathology (PlantVillage, Kaggle Cotton). Strengths: hierarchical feature abstraction from edges to necrotic lesions.
- **Data Leakage in Plant Pathology Datasets**: Recent academic literature highlights that up to 70% of published plant pathology papers fail to isolate photographed plants across train and test sets, leading to severe performance overestimation.
- **Few-Shot Learning Paradigm**: Few-Shot Learning (FSL) using Metric Learning (Siamese Networks, Prototypical Networks) addresses data scarcity by training models to discern morphological similarity rather than static closed-set classification. (Evaluated as a future progression beyond the Phase 1 transfer learning baseline).

### 5. Dataset Description & Forensic Audit Findings

Exhaustive audit across the workspace uncovered 14,955 raw files across two source directories: `Cotton/Original Dataset` and `Cotton/Augmented Dataset`.

#### Canonical Classes & Verified Distribution
1. **Alternaria Leaf Spot** (`Alternaria_Leaf`): Fungal concentric target-like brown necrotic spots.
2. **Aphids** (`Aphids`): Homopteran insect colonies infesting leaf undersides causing curling.
3. **Army Worm** (`Army_worm`): Noctuid larval chewing damage and skeletonized foliar margins.
4. **Bacterial Blight** (`Bacterial_Blight`): *Xanthomonas citri* pv. *malvacearum* causing angular water-soaked leaf spots.
5. **Fusarium Wilt** (`Fusarium_Wilt`): Vascular wilt causing interveinal chlorosis, vascular browning, and foliar desiccation.
6. **Healthy Leaf** (`Healthy_Leaf`): Vigorous, unblemished cotton foliage.
7. **Powdery Mildew** (`Powdery_Mildew`): *Leveillula taurica* producing white powdery mycelial patches.
8. **Target Spot** (`Target_spot`): *Corynespora cassiicola* producing concentric circular necrotic rings.
9. **Verticillium Wilt** (`Verticillium_Wilt`): Vascular fungus causing characteristic "tiger-stripe" foliar chlorosis.

#### Critical Forensic Discoveries
- **OS Artifacts Purged**: 4 macOS `.DS_Store` metadata files identified and removed.
- **Cross-Class Label Clashes**: 14 files possessing identical cryptographic MD5 hashes were labeled under conflicting disease tags in the online dataset. These were purged to ensure absolute ground-truth purity.
- **Kaggle Pre-Augmentation Clumping**: In classes such as *Aphids*, *Army Worm*, *Powdery Mildew*, and *Target Spot*, the source folder contained only ~35 to 45 unique physical leaves, each synthetically augmented into 30 to 42 transformed copies (prefixed with `rotation_`, `contrast_`, `crop_`, `flip_`).

### 6. Proposed Methodology

```
+-------------------------------------------------------------+
|              Raw Dataset (14,955 Files)                     |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|      Forensic Audit: MD5 Hashing & Corruption Check         |
|   (Purged 4 .DS_Store, Purged 14 Cross-Class Clashes)       |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|    Disjoint Set Union (DSU) Leaf & Hash Connected Cluster   |
|            5,852 Strictly Isolated Leaf Clusters            |
+-------------------------------------------------------------+
                              |
             +----------------+----------------+
             | Stratified Group Cluster Split  |
             +----------------+----------------+
             |                |                |
             v                v                v
      Train Clusters     Val Clusters     Test Clusters
         (~70%)             (~15%)           (~15%)
      10,418 images       887 images       872 images
             |                |                |
             v                |                |
+--------------------------+  |                |
| Training-Only Augment    |  |                |
| H-Flip, +/-15° Rotate,   |  |                |
| Brightness, Contrast     |  |                |
+--------------------------+  |                |
             |                |                |
             v                v                v
+-------------------------------------------------------------+
|      MobileNetV2 Transfer Learning (ImageNet Weights)       |
|    Frozen Backbone + Dropout(0.3) + Linear Classification   |
|         Balanced Class Weights Cross-Entropy Loss           |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|     Untouched Test Set Evaluation & Error Analysis          |
|      Macro-F1, Confusion Matrix, Misclassified Audit        |
+-------------------------------------------------------------+
```

### 7. Implementation Details
- **Programming Language**: Python 3.12 (Windows PowerShell environment).
- **Core Libraries**: PyTorch 2.14, TorchVision 0.29, Scikit-Learn 1.9, Pandas 2.3, Pillow 12.3, Matplotlib 3.11, Seaborn 0.13.
- **Feature Extractor**: MobileNetV2 (Sandler et al., CVPR 2018), inverted residual blocks with linear bottlenecks.
- **Hyperparameters**:
  - Input resolution: 224 x 224 x 3.
  - Initial learning rate: $1 \times 10^{-3}$ (Adam optimizer).
  - Batch size: 32.
  - Dropout probability: 0.30.
  - Regularization: Inverse frequency class weights:
    $$W_c = \frac{N_{total}}{K \cdot N_c}$$

### 8. Experimental Results & Verification
The MobileNetV2 transfer learning baseline was evaluated on the untouched test partition ($N = 871$ clean, isolated test leaves) across all 9 classes.

#### Quantitative Test Set Performance
- **Overall Test Accuracy**: **89.90%** (783 / 871 correctly classified)
- **Macro F1-Score**: **0.8741**
- **Weighted F1-Score**: **0.8966**
- **Macro Precision**: **0.8660**
- **Macro Recall**: **0.8905**
- **Total Misclassifications**: 88 images (10.10%)

#### Class-Wise Breakdown on Untouched Test Leaves
| Disease / Pest Class | Precision | Recall | F1-Score | Test Samples |
| :--- | :---: | :---: | :---: | :---: |
| **Alternaria Leaf** | 0.9150 | 0.9459 | 0.9302 | 148 |
| **Aphids** | 0.8077 | 0.9130 | 0.8571 | 23 |
| **Army Worm** | 0.8947 | 0.8500 | 0.8718 | 20 |
| **Bacterial Blight** | 0.9683 | 0.6971 | 0.8106 | 175 |
| **Fusarium Wilt** | 0.8645 | 0.9437 | 0.9024 | 142 |
| **Healthy Leaf** | 0.9774 | 0.9943 | 0.9858 | 174 |
| **Powdery Mildew** | 0.7826 | 0.9000 | 0.8372 | 20 |
| **Target Spot** | 0.7500 | 0.8182 | 0.7826 | 22 |
| **Verticillium Wilt** | 0.8333 | 0.9524 | 0.8889 | 147 |

- **Data Leakage Verification**: Automated cryptographic hash intersection tests across Train, Validation, and Test sets confirmed zero overlap ($|Train \cap Test| = 0$).
- **Distinction Between Validation and Test**: Validation accuracy during checkpointing peaked at 90.40%, closely aligning with the final untouched test accuracy of 89.90%, demonstrating healthy generalization without memorization.

### 9. Limitations & Field Generalization Challenges
1. **Laboratory vs. Field Disconnect**: Online images typically isolate clean, well-lit leaves against plain backgrounds. In Dhule fields, leaves are obscured by weeds, dust, shadows, overlapping foliage, and co-occurring nutrient deficiencies.
2. **Transfer Learning vs. Few-Shot Learning**: MobileNetV2 requires representative training instances across all 9 classes. In true few-shot agricultural scenarios where novel pests emerge (e.g., Pink Bollworm outbreaks), episodic meta-learning or self-supervised vision transformers are required.

### 10. Conclusion & Future Work for Dhule Region
Phase 1 successfully built an audited, scientifically reproducible, and leak-free computer vision baseline for cotton foliar diseases. 

**Roadmap for Phase 2 (Dhule Regional Field Deployment)**:
1. **On-Site Field Data Acquisition**: Partner with agricultural colleges (e.g., College of Agriculture, Dhule under MPKV Rahuri) and Krishi Vigyan Kendra (KVK) Dhule to photograph real cotton leaves under fluctuating field conditions.
2. **Out-of-Distribution (OOD) Testing**: Benchmark the Phase 1 model against Dhule field images to quantify domain shift degradation.
3. **Few-Shot Domain Adaptation**: Implement Prototypical Networks to adapt the model to localized Dhule disease manifestations with fewer than 10 field shots per class.
4. **Edge Optimization**: Quantize the model (INT8 ONNX/TFLite) for low-power edge deployment on Android devices without internet dependency in remote farm fields.

---
### 11. References
1. Sandler, M., Howard, A., Zhu, M., Zhmoginov, A., & Chen, L. C. (2018). MobileNetV2: Inverted Residuals and Linear Bottlenecks. *IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 4510-4520.
2. Hughes, D., & Salathé, M. (2015). An open access repository of images on plant health to enable the development of mobile disease diagnostics. *arXiv preprint arXiv:1511.08060*.
3. Barbedo, J. G. A. (2018). Factors influencing the use of deep learning for plant disease recognition. *Biosystems Engineering*, 172, 84-91.
4. Mohanty, S. P., Hughes, D. P., & Salathé, M. (2016). Using deep learning for image-based plant disease detection. *Frontiers in Plant Science*, 7, 1419.
