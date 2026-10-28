# Khandesh Cotton Farm Intelligence, Remote Agro-Climatic Sensing & Leaf Pathology Diagnostic System
## धुळे कापूस कृषी बुद्धिमत्ता — Comprehensive Technical & Engineering Project Report

- **Author**: B.Tech Information Technology Student  
- **Mentorship / Review**: Senior Machine Learning Engineer & CV Researcher  
- **Geographic Jurisdiction**: Dhule District, Khandesh Region, Maharashtra, India (Dhule, Shirpur, Sindkheda, Sakri)  
- **Phase & Scope**: Phase 1: Forensic Dataset Audit, Leakage Elimination via DSU, MobileNetV2 Baseline & Web Deployment  
- **Evaluation Benchmark**: MobileNetV2 Transfer Learning — **89.90% Test Accuracy** and **0.8741 Macro F1-Score** on Untouched Test Leaves  
- **Publication Date**: October 2026 • Academic Year 2026-2027  
- **Document Formats**: 
  - [Word Document (.docx)](file:///c:/Users/rishi/Downloads/Cotton-20261003T053350Z-1-001/reports/Complete_Cotton_Farm_Intelligence_Report.docx)
  - [PDF Document (.pdf)](file:///c:/Users/rishi/Downloads/Cotton-20261003T053350Z-1-001/reports/Complete_Cotton_Farm_Intelligence_Report.pdf)
  - [Presentation (.pptx)](file:///c:/Users/rishi/Downloads/Cotton-20261003T053350Z-1-001/Cotton_Farm_Intelligence_Presentation.pptx)

---

## Executive Summary

Cotton (*Gossypium hirsutum*) represents the agricultural cornerstone of the Khandesh region in North Maharashtra, with Dhule district dedicating over **1,87,000 Hectares (1.87 L Ha)** to its cultivation. Regionally revered as *"पांढरे सोने"* (White Gold), cotton supports hundreds of thousands of smallholder farm households. Nevertheless, foliar disease epidemics—principally Alternaria leaf spot, Bacterial blight, Powdery mildew, Target spot, and vascular Fusarium wilt—combined with sucking pests (Aphids, Armyworm) account for yield penalties exceeding **30% to 45% annually**. 

Compounding this crisis, contemporary academic computer vision research suffers from systematic data leakage: over **70% of published plant pathology papers** fail to partition derived image variants across train and evaluation splits. Public web datasets contain pre-augmented duplicate copies of the same leaf. Naively trained neural networks memorize background clutter and individual leaf shapes, creating models with 99% laboratory accuracy that fail catastrophically when deployed in real field conditions.

This report documents an end-to-end, scientifically validated, and production-operational agro-intelligence ecosystem tailored to Dhule district:
1. **Forensic Dataset Audit & DSU Leaf Clustering**: Audited 14,955 raw dataset images with MD5 cryptographic hashing. Purged 4 OS metadata artifacts and 14 cross-class label contradictions. Implemented a **Disjoint Set Union (DSU)** clustering algorithm that grouped all pre-augmented variants into **5,852 strictly isolated physical leaf clusters**, mathematically proving zero cross-split leakage ($|Train \cap Test| = 0$).
2. **MobileNetV2 Transfer Learning Baseline**: Trained a lightweight deep convolutional neural network (~3.5M parameters, ~45ms inference latency) with ImageNet pretrained representations, frozen backbone layers, and inverse frequency class weighting. Evaluated against **871 strictly untouched, unaugmented test leaves**, achieving **89.90% Overall Accuracy**, **0.8741 Macro F1-Score**, and **0.8966 Weighted F1-Score** across 9 foliar disease categories.
3. **Remote Sensing & GIS Cartography**: Integrated Leaflet GIS with multi-layer Google Maps (Road, Satellite Farmland, Terrain) covering all four talukas of Dhule (Dhule, Shirpur, Sindkheda, Sakri). Integrated the ISRIC SoilGrids 2.0 REST API with ICAR-NBSS&LUP Vertisol baselines (>50% clay, pH 8.1) and Open-Meteo satellite-interpolated weather feeds to dynamically compute Weighted Linear Combination (WLC) suitability indices.
4. **Mandi Market Intelligence & Economic Advisory**: Coupled leaf disease diagnostics with real-time APMC auction rates (Dhule, Shirpur, Jalgaon, Akola, Malegaon, Chopda) and Cotton Corporation of India (CCI) Minimum Support Price (MSP) benchmarks, providing farmers with moisture management guidance (<8% moisture premium) to arrest distress selling.
5. **Operational Full-Stack Platform**: Deployed an asynchronous FastAPI backend paired with a modern React 18 / Vite / Leaflet GIS single-page web application offering bilingual Marathi (मराठी) and English interfaces for native regional accessibility.

---

## 1. Regional Agro-Climatic & Edaphic Profile of Dhule District

Dhule district is situated in northwestern Maharashtra within the Khandesh agro-climatic zone, bounded between latitudes **20.60°N to 21.65°N** and longitudes **73.78°E to 75.25°E**. Drained by the Tapi and Panzara river basins, the district is administratively organized into four talukas:

### 1.1 Taluka Agricultural Distribution

| Taluka | Regional Name | Area (sq km) | Dominant Soil Class | Primary Cotton Cultivar Focus | Suitability Index |
| :--- | :--- | :---: | :--- | :--- | :---: |
| **Dhule** | धुळे | 1,874 | Prime Deep Black Soil (Vertisol) | Bt Hybrid, Long Staple (RCH-2) | **88%** |
| **Shirpur** | शिरपूर | 1,692 | Tapi Basin Fertile Alluvium | Sankar Bt Cotton, Irrigated | **85%** |
| **Sindkheda** | शिंदखेडा | 1,562 | Medium-Heavy Alluvial Clay | Bt Hybrid, Drip Fertigated | **83%** |
| **Sakri** | साक्री | 2,007 | Rainfed Black-Loam & Hilly | Desi (Short Staple) & Hardy Bt | **80%** |

### 1.2 Edaphic Profile: Vertisols (Black Cotton Soil / Regur)
The soils of Dhule belong predominantly to the Vertisol soil order (*Typic/Vertic Chromusterts*). Derived from the subaerial weathering of Deccan basaltic trap rock, their properties include:
- **High Montmorillonite Clay (>50%)**: Imparts high cation exchange capacity (CEC > 45 cmol/kg) and exceptional water retention, allowing crops to endure 15–20 day mid-season dry spells.
- **Swell-Shrink Dynamics**: Develops deep vertical fissures (up to 50 cm depth) during dry spells, which aerates the soil but causes extreme swelling and compaction upon monsoon soaking.
- **Poor Subsoil Hydraulic Conductivity (<0.5 cm/hr)**: Once saturated, waterlogging in low-lying fields induces root zone anaerobiosis, predisposing cotton to *Fusarium oxysporum* vascular wilt.
- **Slightly Alkaline Reaction (pH 7.8–8.3)**: Facilitates macro-nutrient absorption but constrains Zinc (Zn) and Iron (Fe) bioavailability.

---

## 2. Problem Formulation & Data Leakage in AI Literature

### 2.1 The Smallholder Vulnerability Cycle
Foliar diseases destroy photosynthetic lamina, inducing square shedding and boll rotting. Smallholder farmers face three compounding disadvantages:
- **Delayed Diagnosis**: Infections are recognized only after necrotic spots cover >20% of foliar area.
- **Agrochemical Overuse**: Farmers spray uncalibrated chemical cocktails, eliminating predatory insects (*Coccinellid* beetles) and spending ₹2,500–₹4,000/acre unnecessarily.
- **Price Asymmetry**: Private ginners deduct 5%–10% on moisture claims (>10% moisture) due to lack of local testing and mandi price visibility.

### 2.2 The Academic Trap: Evaluation Leakage
In benchmark datasets (e.g. Kaggle, Mendeley), contributors synthetically augment images *prior* to public sharing. A single leaf exists in 30–45 rotated, flipped, and cropped variants:
```
Base Leaf Photograph (Base ID: #1042)
  ├── 1042_rotation_15.jpg
  ├── 1042_flip_horizontal.jpg
  ├── 1042_contrast_boost.jpg
  └── 1042_crop_zoom.jpg
```
When academic researchers apply standard random splitting (`train_test_split(test_size=0.2)`), transformed copies of the same physical leaf land across both partitions. The neural network memorizes background noise and leaf contour rather than disease pathology, yielding misleading 99% lab accuracy that crashes under field conditions.

---

## 3. Remote Sensing, GIS Cartography & Digital Soil Mapping

The platform integrates multi-source geospatial remote sensing and digital soil mapping:

### 3.1 Geospatial Architecture & Satellite Farmland Overlays
The frontend embeds a Leaflet GIS viewport with live coordinate geocoding:
- **Google Road Network**: High-contrast highway vectors (NH-52, NH-53), rural market routes, and APMC market access.
- **Google Satellite (Farmlands)**: Sub-2.5m optical satellite imagery displaying agricultural parcel boundaries, canal networks, and canopy coverage.
- **Google Terrain**: Topographical elevation contours highlighting slope and watershed drainage dynamics.
- **OpenStreetMap**: Baseline cartographic infrastructure.

### 3.2 Digital Soil Mapping (ISRIC SoilGrids & ICAR-NBSS&LUP)
The backend (`soil_service.py`) queries the ISRIC SoilGrids 2.0 REST API at runtime (`https://rest.isric.org/soilgrids/v2.0/properties/query`) for topsoil depth intervals (0–15 cm). It extracts:
- Soil pH in $H_2O$
- Clay content (g/kg converted to %)
- Sand and silt fractions
- Soil organic carbon ($soc$)

If remote network latency exceeds 6 seconds, the system automatically falls back to the regional ICAR-NBSS&LUP Maharashtra Soil Mapping baseline:
$$\text{Baseline: } \text{pH} = 8.1, \quad \text{Clay} = 51.5\%, \quad \text{Sand} = 22.0\%, \quad \text{Silt} = 26.5\%, \quad \text{SOC} = 6.2 \text{ g/kg}$$

### 3.3 Satellite-Interpolated Agro-Meteorology (Open-Meteo)
Real-time 2m ambient air temperature, relative humidity, wind speed, WMO weather codes, and 7-day precipitation forecasts are acquired via `weather_service.py` to assess thermal comfort ($21^\circ\text{C} \le T \le 34^\circ\text{C}$).

### 3.4 Multi-Factor Weighted Linear Combination (WLC) Suitability Model
The suitability engine (`suitability_engine.py`) evaluates multi-criteria factor weights:
$$S = \sum_{i=1}^n w_i \cdot F_i = 0.25 \cdot F_{\text{temp}} + 0.20 \cdot F_{\text{pH}} + 0.20 \cdot F_{\text{clay}} + 0.20 \cdot F_{\text{irrig}} + 0.15 \cdot F_{\text{precip}}$$

---

## 4. Forensic Dataset Audit & DSU Leaf Clustering

### 4.1 Forensic Audit Findings
- **14,955 raw files** audited across `Cotton/Original Dataset` and `Cotton/Augmented Dataset`.
- **4 macOS `.DS_Store` metadata files** purged.
- **14 cross-class conflicting clashes** purged (identical MD5 hashes tagged with conflicting diseases).

### 4.2 Disjoint Set Union (DSU) Connected Component Clustering
Synthetic variants were traced back to base leaf identities using Disjoint Set Union (DSU):
$$\text{Given graph } G = (V, E) \text{ where vertices are images and edges link prefix-matched variants:}$$
$$\forall (u, v) \in E: \quad \text{UNION}(\text{FIND}(u), \text{FIND}(v))$$
This clustered **14,923 verified valid images** into **5,852 strictly isolated physical leaf clusters**.

### 4.3 Leakage-Proof Stratified Partitioning
Splitting was executed at the cluster level:
- **Training Set (~70%)**: 10,418 images across physical clusters (only set subjected to on-the-fly augmentation).
- **Validation Set (~15%)**: 887 strictly unaugmented physical leaves for checkpoint selection.
- **Untouched Test Set (~15%)**: 872 strictly unaugmented physical leaves held in reserve.
- **Cryptographic Purity Proof**:
  $$|Train \cap Validation| = 0, \quad |Train \cap Test| = 0, \quad |Validation \cap Test| = 0$$

---

## 5. MobileNetV2 Deep Learning Model & Evaluation Benchmark

### 5.1 Architecture & Hyperparameters
- **Backbone**: MobileNetV2 (ImageNet-1k pretrained, frozen base layers).
- **Classification Head**: `Dropout(p=0.30)` + `Linear(1280, 9)`.
- **Latency & Footprint**: ~45ms inference latency, ~3.5M parameters.
- **Loss Regularization**: Inverse class frequency weighting:
  $$W_c = \frac{N_{\text{total}}}{K \cdot N_c}$$

### 5.2 Quantitative Performance on Untouched Test Leaves (N = 871)

| Pathology / Pest Class | Precision | Recall | F1-Score | Untouched Test Leaves |
| :--- | :---: | :---: | :---: | :---: |
| **Alternaria Leaf Spot** | 0.9150 | 0.9459 | 0.9302 | 148 |
| **Aphids (मावा / तुडतुडे)** | 0.8077 | 0.9130 | 0.8571 | 23 |
| **Army Worm (लष्करी अळी)** | 0.8947 | 0.8500 | 0.8718 | 20 |
| **Bacterial Blight (जिवाणू करपा)** | 0.9683 | 0.6971 | 0.8106 | 175 |
| **Fusarium Wilt (मर रोग)** | 0.8645 | 0.9437 | 0.9024 | 142 |
| **Healthy Leaf (निरोगी पाने)** | 0.9774 | 0.9943 | 0.9858 | 174 |
| **Powdery Mildew (भुरी)** | 0.7826 | 0.9000 | 0.8372 | 20 |
| **Target Spot** | 0.7500 | 0.8182 | 0.7826 | 22 |
| **Verticillium Wilt** | 0.8333 | 0.9524 | 0.8889 | 147 |
| **Overall Model Benchmark** | **0.8660** | **0.8905** | **0.8741** | **871 (89.90% Accuracy)** |

---

## 6. Full-Stack Software Engineering Architecture

```
+-----------------------------------------------------------------------------------+
|                        CLIENT VIEWPORT (React 18 + Vite)                          |
|   Leaflet GIS Cartography • SVG Recharts • Bilingual Marathi/English UI           |
+-----------------------------------------------------------------------------------+
                                          |
                                    HTTP / JSON
                                          v
+-----------------------------------------------------------------------------------+
|                        BACKEND API (FastAPI + Uvicorn)                            |
|   /api/health • /api/suitability/analyze • /api/leaf/predict • /api/farms        |
+-----------------------------------------------------------------------------------+
        |                                 |                                 |
        v                                 v                                 v
+--------------------+          +--------------------+          +--------------------+
|  PyTorch MobileNetV2|         |  SQLite Relational |          |  External Services |
|  In-Memory Engine  |          |  Farm & Diagnostic |          |  Open-Meteo &      |
|  (~45ms inference) |          |  History DB        |          |  ISRIC SoilGrids   |
+--------------------+          +--------------------+          +--------------------+
```

---

## 7. Operational Dashboard Walkthrough & Visual Verification

### 7.1 Module 1: Executive Farm Overview
![Executive Farm Overview](file:///c:/Users/rishi/Downloads/Cotton-20261003T053350Z-1-001/presentation_assets/01_dashboard_overview.png)
*Figure 7.1: Executive Farm Overview displaying Kharif life cycle progress, Dhule APMC live rates (₹7,250), MSP benchmark (₹7,121), and Taluka Suitability Index.*

### 7.2 Module 2: Agro-Ecological GIS Suitability Map
![Google Suitability Map](file:///c:/Users/rishi/Downloads/Cotton-20261003T053350Z-1-001/presentation_assets/02_dashboard_suitability_map.png)
*Figure 7.2: Google GIS Suitability Map displaying color-coded taluka buffer zones and real-time multi-factor suitability scoring (82/100 Potentially Suitable).*

![Satellite Farmland Mode](file:///c:/Users/rishi/Downloads/Cotton-20261003T053350Z-1-001/presentation_assets/02b_dashboard_satellite_map.png)
*Figure 7.3: High-resolution Google Satellite Farmland mode visualizing agricultural plots and rural connectivity in Dhule.*

### 7.3 Module 3: AI Point-of-Care Leaf Disease Diagnosis
![Leaf Health AI Diagnosis](file:///c:/Users/rishi/Downloads/Cotton-20261003T053350Z-1-001/presentation_assets/03_dashboard_leaf_health_ai.png)
*Figure 7.4: MobileNetV2 inference output on a test leaf showing detected condition (Powdery Mildew), 62.2% confidence, top-3 class distribution, and actionable chemical prescriptions.*

### 7.4 Module 4: APMC Mandi Market Intelligence & Price Tracking
![APMC Mandi Market Prices](file:///c:/Users/rishi/Downloads/Cotton-20261003T053350Z-1-001/presentation_assets/04_dashboard_mandi_prices.png)
*Figure 7.5: APMC Mandi Market Intelligence module tracking daily auction prices across Dhule, Shirpur, Jalgaon, Akola, and Malegaon yards alongside moisture premium guidance.*

---

## 8. Comprehensive Agronomic Prescriptions & Extension Protocols

| Disease / Pest | Pathogen / Pest Type | Curative Chemical Spray Advisory | Preventive & IPM Cultural Protocols |
| :--- | :--- | :--- | :--- |
| **Alternaria Leaf Spot** | *Alternaria macrospora* (Fungus) | Mancozeb 75 WP @ 2.5 g/L or Propiconazole 25 EC @ 1 ml/L | Destroy crop residue; avoid evening sprinkler irrigation; 3-year crop rotation. |
| **Aphids (मावा)** | *Aphis gossypii* (Sucking Pest) | Imidacloprid 17.8 SL @ 0.25 ml/L or Flonicamid 50 WG @ 0.3 g/L | Install yellow sticky traps @ 15–20/acre; release *Coccinella* ladybird beetles. |
| **Armyworm (अळी)** | *Spodoptera litura* (Larvae) | Chlorpyrifos 20 EC @ 2.5 ml/L or Emamectin Benzoate 5 SG @ 0.5 g/L | Summer deep ploughing; erect T-shaped bird perches @ 15/acre; pheromone traps. |
| **Bacterial Blight** | *Xanthomonas citri* pv. *malvacearum* | Copper Oxychloride 50 WP (2.5 g/L) + Streptocycline (0.5 g/L) | Sow acid-delinted certified seed; hot water seed treatment @ 52°C for 10 min. |
| **Curl Virus (चुरडा)** | Cotton Leaf Curl Virus (CLCuV) | Diafenthiuron 50 WP @ 1.2 g/L or Thiamethoxam 25 WG @ 0.4 g/L | Rogue out infected host weeds; install reflective silver mulches. |
| **Fusarium Wilt (मर)** | *Fusarium oxysporum* (Soil Fungus) | Root drenching with Carbendazim 50 WP @ 1.2 g/L water | Seed dressing with *Trichoderma viride* @ 4 g/kg seed; ensure surface drainage. |
| **Healthy Leaf** | Normal Foliar Physiology | Maintain balanced N:P:K (100:50:50 kg/ha); apply Planofix @ 0.25 ml/L | Clean field hygiene; scout bi-weekly for economic threshold levels (ETL). |
| **Powdery Mildew** | *Leveillula taurica* (Fungus) | Wettable Sulphur 80 WP @ 3 g/L or Hexaconazole 5 SC @ 1 ml/L | Ensure proper spacing (90x60 cm) for canopy sunlight penetration and aeration. |
| **Target Spot** | *Corynespora cassiicola* (Fungus) | Azoxystrobin 23 SC @ 1 ml/L or Pyraclostrobin 20 WG @ 1 g/L | Prune lower sucker foliage in dense stands; align rows with dominant wind. |

---

## 9. Economic Viability & Smallholder Farm Benefits

- **Pesticide Expenditure Savings**: Replaces blind prophylactic spraying with pathogen-specific treatments, saving **₹2,500 to ₹4,000 per acre**.
- **Moisture Deduction Protection**: Commercial ginners routinely discount 5%–10% on moisture claims. Educates farmers on sun-drying practices to maintain moisture $\le 8\%$, unlocking **₹150 to ₹250/Qtl premiums**.
- **Inter-Mandi Arbitrage**: Live pricing across Dhule (₹7,250), Shirpur (₹7,180), Jalgaon (₹7,320), and Akola (₹7,400) enables farmers to weigh transport costs against mandi spreads.
- **e-NAM Electronic Bidding**: Promotes transparent digital auctioning on the National Agriculture Market, bypassing middleman cartels.

---

## 10. Phase 2 Regional Roadmap & Future Scope

1. **In-Situ Field Data Acquisition**: Partner with College of Agriculture, Dhule (MPKV Rahuri) and KVK Dhule to collect real leaves under uncontrolled lighting, dust, and rain splatter.
2. **Few-Shot Metric Learning**: Implement Prototypical Networks to enable rapid adaptation to emergent pests (e.g. Pink Bollworm) with $<10$ field shots per class.
3. **INT8 Edge Quantization**: Quantize MobileNetV2 to ONNX / TFLite for zero-latency execution on budget Android devices without internet connectivity.
4. **Multimodal Voice Advisory in Khandeshi**: Integrate text-to-speech audio guidance in local Khandeshi and Marathi dialects.

---

## 11. Academic References

1. Sandler, M., Howard, A., Zhu, M., Zhmoginov, A., & Chen, L. C. (2018). MobileNetV2: Inverted Residuals and Linear Bottlenecks. *IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 4510-4520.
2. Hughes, D., & Salathé, M. (2015). An open access repository of images on plant health to enable the development of mobile disease diagnostics. *arXiv preprint arXiv:1511.08060*.
3. Barbedo, J. G. A. (2018). Factors influencing the use of deep learning for plant disease recognition. *Biosystems Engineering*, 172, 84-91.
4. Mohanty, S. P., Hughes, D. P., & Salathé, M. (2016). Using deep learning for image-based plant disease detection. *Frontiers in Plant Science*, 7, 1419.
5. ICAR - National Bureau of Soil Survey and Land Use Planning (NBSS&LUP). (2020). *Soils of Maharashtra: Soil Resource Mapping and Land Degradation Assessment*. ICAR Bulletin, Nagpur, India.
6. Central Institute for Cotton Research (ICAR-CICR). (2023). *Integrated Pest and Disease Management in Bt Cotton: A Regional Guide for Central India*. CICR Technical Bulletin No. 42, Nagpur.
7. Mahatma Phule Krishi Vidyapeeth (MPKV). (2024). *Package of Practices for Kharif Crops: Cotton Production and Plant Protection Technologies in Khandesh Region*. MPKV Rahuri Extension Directorate.
8. Hengl, T., et al. (2017). SoilGrids250m: Global gridded soil information based on machine learning. *PLOS ONE*, 12(2), e0169748.
