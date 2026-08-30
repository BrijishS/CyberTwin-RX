import os
import json
import joblib
import pandas as pd
from typing import Dict, Any, List, Union

from backend.ai.train_model import MODEL_FILE, METADATA_FILE, train_and_save_model, FEATURE_COLUMNS

FRIENDLY_FEATURE_NAMES = {
    "epss_score": "EPSS score",
    "cvss_score": "CVSS score",
    "kev_status": "Known Exploited Vulnerability (KEV)",
    "internet_exposed": "Internet exposure",
    "patch_available": "Patch availability status",
    "asset_criticality": "Asset criticality level",
    "control_effectiveness": "Security control effectiveness",
    "open_vulnerability_count": "Open vulnerability count",
    "high_vulnerability_count": "High CVSS vulnerability density",
    "business_criticality": "Business service criticality",
}


class ExploitPredictor:
    def __init__(self):
        self.model = None
        self.metadata = {}
        self.is_loaded = False
        self._load_model()

    def _load_model(self):
        try:
            if not os.path.exists(MODEL_FILE) or not os.path.exists(METADATA_FILE):
                print("ML Model or metadata missing. Training model automatically...")
                self.metadata = train_and_save_model()

            self.model = joblib.load(MODEL_FILE)
            with open(METADATA_FILE, "r") as f:
                self.metadata = json.load(f)
            self.is_loaded = True
        except Exception as e:
            print(f"Error loading ML Exploit Model: {e}")
            self.model = None
            self.metadata = {}
            self.is_loaded = False

    def get_status(self) -> Dict[str, Any]:
        if not self.is_loaded:
            return {
                "loaded": False,
                "model": "RandomForestClassifier (Not Loaded)",
                "error": "Model file not found or failed to load",
            }
        return {
            "loaded": True,
            "model": self.metadata.get("model_name", "RandomForestClassifier"),
            "dataset": self.metadata.get("dataset_type", "Synthetic prototype dataset"),
            "training_samples": self.metadata.get("training_samples", 5000),
            "training_date": self.metadata.get("training_date", "Unknown"),
            "metrics": self.metadata.get("metrics", {}),
            "feature_importances": self.metadata.get("feature_importances", {}),
        }

    def predict(self, features: Union[Dict[str, Any], pd.DataFrame]) -> Dict[str, Any]:
        if not self.is_loaded or self.model is None:
            self._load_model()
            if not self.is_loaded:
                raise RuntimeError("Exploit Prediction ML Model is not loaded.")

        if isinstance(features, dict):
            df = pd.DataFrame([features])[FEATURE_COLUMNS]
        else:
            df = features[FEATURE_COLUMNS]

        # Predict exploitation probability using Random Forest predict_proba
        proba = float(self.model.predict_proba(df)[0][1])
        proba = min(max(proba, 0.0), 1.0)
        percentage = round(proba * 100.0, 1)

        # Categorize Risk Level
        if percentage <= 25.0:
            risk_level = "Low"
        elif percentage <= 50.0:
            risk_level = "Moderate"
        elif percentage <= 75.0:
            risk_level = "High"
        else:
            risk_level = "Critical"

        # Model Confidence based on probability distance from 0.5
        dist = abs(proba - 0.5) * 2.0
        if dist >= 0.55:
            confidence = "High"
        elif dist >= 0.25:
            confidence = "Medium"
        else:
            confidence = "Low"

        # Top Contributing Features based on Feature Importance
        feat_importances = self.metadata.get("feature_importances", {})
        top_features = []
        for feat, imp in sorted(feat_importances.items(), key=lambda x: x[1], reverse=True):
            friendly = FRIENDLY_FEATURE_NAMES.get(feat, feat)
            top_features.append(friendly)
            if len(top_features) >= 3:
                break

        return {
            "exploitation_probability": round(proba, 4),
            "percentage": percentage,
            "risk_level": risk_level,
            "confidence": confidence,
            "top_contributing_features": top_features,
        }


# Singleton Predictor Instance
predictor = ExploitPredictor()
