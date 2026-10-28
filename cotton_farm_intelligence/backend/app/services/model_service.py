"""
Cotton Leaf Disease Inference Service.
Connects directly to the Phase 1 trained MobileNetV2 PyTorch model.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import mobilenet_v2

# Agronomic Disease Knowledge Base (CICR / MPKV Rahuri cotton management)
DISEASE_METADATA = {
    "Alternaria_Leaf": {
        "name": "Alternaria Leaf Spot",
        "pathogen": "Alternaria macrospora / alternata (Fungus)",
        "symptoms": "Brown circular necrotic spots with concentric rings ('target board' symptom), leaf blighting, premature defoliation.",
        "advisory": "Remove and burn crop residues. Avoid sprinkler irrigation during evening hours. Apply protective fungicide such as Mancozeb 75 WP (2.5 g/L) or Propiconazole 25 EC (1 ml/L) upon initial lesion detection."
    },
    "Aphids": {
        "name": "Cotton Aphid Infestation",
        "pathogen": "Aphis gossypii (Sucking Insect Pest)",
        "symptoms": "Yellowing, curling, and crinkling of tender leaves; honeydew secretion leading to black sooty mold on leaf surfaces.",
        "advisory": "Monitor economic threshold level (ETL > 10% affected plants). Conserve natural predators (Coccinellid beetles, Chrysoperla). Spray 5% Neem Seed Kernel Extract (NSKE) or systemic insecticide (Acetamiprid 20 SP or Flonicamid 50 WG) as per State Agronomy Dept guidelines."
    },
    "Army_worm": {
        "name": "Fall / Tobacco Armyworm",
        "pathogen": "Spodoptera litura / frugiperda (Lepidopteran Pest)",
        "symptoms": "Irregular skeletonized leaf margins, window-pane feeding holes, and visible larval frass on foliage.",
        "advisory": "Install pheromone traps (5 per acre). Hand-pick egg masses and early-instar clustered larvae. Apply Bacillus thuringiensis (Bt) or Spinosad 45 SC (0.3 ml/L) when larval threshold is crossed."
    },
    "Bacterial_Blight": {
        "name": "Bacterial Blight / Angular Leaf Spot",
        "pathogen": "Xanthomonas citri pv. malvacearum (Bacterium)",
        "symptoms": "Angular water-soaked lesions delineated by leaf veins, turning brown/black; potential petiole infection ('black arm').",
        "advisory": "Spray Copper Oxychloride 50 WP (2.5 g/L) mixed with Streptocycline (100 mg/L) at 10-15 day intervals. Avoid mechanical field operations when foliage is wet to prevent bacterial transmission."
    },
    "Fusarium_Wilt": {
        "name": "Fusarium Wilt",
        "pathogen": "Fusarium oxysporum f. sp. vasinfectum (Soil-borne Fungus)",
        "symptoms": "Interveinal yellowing, epinasty, vascular browning visible upon stem splitting, and sudden irreversible foliar wilting.",
        "advisory": "Strictly prevent water stagnation in heavy Vertisol plots. Seed treatment with Trichoderma viride (10 g/kg seed). Incorporate bio-fertilizers and maintain high soil organic matter to suppress fungal chlamydospores."
    },
    "Healthy_Leaf": {
        "name": "Healthy Cotton Foliage",
        "pathogen": "None (No foliar pathology detected)",
        "symptoms": "Vigorous green leaf lamina with uniform chlorophyll distribution, intact cuticle, and normal vein architecture.",
        "advisory": "Maintain balanced N-P-K nutrition (recommend 100:50:50 kg/ha for Bt cotton in Dhule). Continue bi-weekly scouting for early sucking pests."
    },
    "Powdery_Mildew": {
        "name": "Powdery Mildew",
        "pathogen": "Leveillula taurica / Erysiphe (Fungus)",
        "symptoms": "White to grayish powdery fungal patches on lower and upper leaf surfaces, chlorosis, and upward leaf curling.",
        "advisory": "Thrives in dry, warm days following humid nights. Spray Wettable Sulphur 80 WP (3 g/L) or Hexaconazole 5 EC (1 ml/L). Ensure proper plant spacing for sunlight penetration."
    },
    "Target_spot": {
        "name": "Target Spot",
        "pathogen": "Corynespora cassiicola (Fungus)",
        "symptoms": "Large concentric circular lesions with distinct brown zonate rings, rapidly advancing in lower dense canopy.",
        "advisory": "Improve canopy ventilation by avoiding excessive nitrogenous fertilizer. Apply Azoxystrobin + Difenoconazole or Pyraclostrobin where approved by local plant protection authorities."
    },
    "Verticillium_Wilt": {
        "name": "Verticillium Wilt",
        "pathogen": "Verticillium dahliae (Soil-borne Fungus)",
        "symptoms": "Characteristic 'tiger-stripe' pattern of interveinal chlorosis and necrosis, vascular discoloration in xylem.",
        "advisory": "Practice long crop rotation with non-hosts like sorghum or pearl millet. Avoid deep inter-cultivation that damages root systems. Use tolerant cotton cultivars suited to heavy soils."
    }
}

class CottonLeafModelService:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.classes = []
        self.class_to_idx = {}
        self.preprocess = None
        self.is_loaded = False
        self.load_error = None
        self._load_model()

    def _load_model(self):
        # Locate Phase 1 model weights and mapping across potential parent structures
        current_dir = Path(__file__).resolve().parent
        potential_roots = [
            current_dir.parents[3], # c:\Users\rishi\Downloads\Cotton-20261003T053350Z-1-001
            current_dir.parents[2], # cotton_farm_intelligence
            Path.cwd(),
            Path.cwd().parent
        ]
        
        model_path = None
        mapping_path = None
        
        for root in potential_roots:
            p_model = root / "phase1_cotton" / "models" / "best_cotton_mobilenetv2.pt"
            p_map = root / "phase1_cotton" / "models" / "class_mapping.json"
            if p_model.exists() and p_map.exists():
                model_path = p_model
                mapping_path = p_map
                break
            # Also check direct models/ folder
            p_model_direct = root / "models" / "best_cotton_mobilenetv2.pt"
            p_map_direct = root / "models" / "class_mapping.json"
            if p_model_direct.exists() and p_map_direct.exists():
                model_path = p_model_direct
                mapping_path = p_map_direct
                break

        if not model_path or not mapping_path:
            self.load_error = f"Model checkpoint not found in any standard project paths."
            print(f"[MODEL SERVICE WARNING] {self.load_error}")
            return

        try:
            with open(mapping_path, "r") as f:
                mapping = json.load(f)
                
            self.classes = mapping["classes"]
            self.class_to_idx = mapping["class_to_idx"]
            num_classes = len(self.classes)

            # Initialize MobileNetV2 architecture
            model = mobilenet_v2(weights=None)
            in_features = model.classifier[1].in_features
            model.classifier = nn.Sequential(
                nn.Dropout(p=0.3),
                nn.Linear(in_features, num_classes)
            )

            # Load trained weights
            checkpoint = torch.load(model_path, map_location=self.device)
            if "model_state_dict" in checkpoint:
                model.load_state_dict(checkpoint["model_state_dict"])
            else:
                model.load_state_dict(checkpoint)
                
            model = model.to(self.device)
            model.eval()
            self.model = model

            # Define Preprocessing
            norm = mapping.get("normalization", {"mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225]})
            self.preprocess = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=norm["mean"], std=norm["std"])
            ])
            self.is_loaded = True
            print(f"[MODEL SERVICE] MobileNetV2 successfully loaded ({num_classes} classes) on {self.device}.")
        except Exception as e:
            self.load_error = f"Failed to instantiate model: {str(e)}"
            print(f"[MODEL SERVICE ERROR] {self.load_error}")

    def predict(self, image: Image.Image) -> Dict[str, Any]:
        if not self.is_loaded:
            raise RuntimeError(f"Model service is not loaded: {self.load_error or 'Unknown error'}")

        # Ensure RGB
        img_rgb = image.convert("RGB")
        tensor = self.preprocess(img_rgb).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.model(tensor)
            probs = torch.softmax(logits, dim=1)[0]

        top_k = min(3, len(self.classes))
        top_probs, top_indices = torch.topk(probs, k=top_k)
        
        top_probs = top_probs.cpu().numpy()
        top_indices = top_indices.cpu().numpy()

        primary_class = self.classes[top_indices[0]]
        primary_confidence = float(top_probs[0]) * 100.0

        top_3_items = []
        for rank, (idx, p) in enumerate(zip(top_indices, top_probs)):
            cls_name = self.classes[idx]
            info = DISEASE_METADATA.get(cls_name, {})
            top_3_items.append({
                "disease_class": cls_name,
                "confidence_percentage": round(float(p) * 100.0, 2),
                "severity_level": "Normal" if cls_name == "Healthy_Leaf" else ("Critical" if "Wilt" in cls_name else "Moderate"),
                "symptom_description": info.get("symptoms", "Foliar pathological manifestation.")
            })

        info_primary = DISEASE_METADATA.get(primary_class, {})
        practical_advice = info_primary.get("advisory", "Consult a certified plant pathologist at KVK Dhule or MPKV Rahuri.")

        return {
            "predicted_class": primary_class,
            "confidence_percentage": round(primary_confidence, 2),
            "top_3_predictions": top_3_items,
            "model_name": "MobileNetV2 (ImageNet Transfer Learning)",
            "model_version": "Phase 1 Baseline Checkpoint (9 Classes)",
            "evaluation_test_accuracy": "89.90% (Measured on 871 untouched test leaves)",
            "practical_next_steps": practical_advice,
            "calibration_caution": "The percentage score represents the model's softmax activation and is not an uncalibrated Bayesian posterior probability.",
            "field_transfer_caution": "This model was trained on benchmark images. Field conditions in Dhule farms (ambient dust, soil splatter, solar glare, co-occurring pests) require localized validation before commercial agrochemical treatment."
        }

# Global singleton instance
_model_instance = None

def get_leaf_model_service() -> CottonLeafModelService:
    global _model_instance
    if _model_instance is None:
        _model_instance = CottonLeafModelService()
    return _model_instance
