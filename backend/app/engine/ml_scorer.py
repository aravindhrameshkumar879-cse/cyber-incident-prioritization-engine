import os
import json
import joblib
import numpy as np
from typing import Dict, Any, Tuple
from app.core.config import settings

INCIDENT_TYPES = [
    "Ransomware",
    "Data Exfiltration",
    "Unauthorized Access",
    "DDoS",
    "Phishing",
    "Malware",
    "Insider Threat",
    "Privilege Escalation",
]

ASSET_TYPES = [
    "Domain Controller",
    "Database Server",
    "Payment Gateway",
    "Cloud Storage",
    "Application Server",
    "Workstation",
    "VPN Gateway",
    "Internal Wiki",
]

INCIDENT_TYPE_MAP = {t: i for i, t in enumerate(INCIDENT_TYPES)}
ASSET_TYPE_MAP = {a: i for i, a in enumerate(ASSET_TYPES)}

FEATURE_COLUMNS = [
    "severity",
    "data_sensitivity",
    "asset_importance",
    "attack_confidence",
    "affected_users_normalized",
    "business_impact",
    "incident_type_encoded",
    "asset_type_encoded",
    "time_risk",
    "historical_frequency",
    "recurrence",
    "affected_system_count_normalized"
]

class MLScorer:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_config = None
        self.evaluation_metrics = None
        self._load_artifacts()

    def _load_artifacts(self):
        models_dir = settings.ML_MODELS_DIR
        model_path = os.path.join(models_dir, "priority_model.pkl")
        scaler_path = os.path.join(models_dir, "scaler.pkl")
        config_path = os.path.join(models_dir, "feature_config.json")
        metrics_path = os.path.join(models_dir, "evaluation_metrics.json")

        if os.path.exists(model_path) and os.path.exists(scaler_path):
            try:
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                if os.path.exists(config_path):
                    with open(config_path, "r") as f:
                        self.feature_config = json.load(f)
                if os.path.exists(metrics_path):
                    with open(metrics_path, "r") as f:
                        self.evaluation_metrics = json.load(f)
                print(f"[MLScorer] Successfully loaded trained model from {model_path}")
            except Exception as e:
                print(f"[MLScorer] Error loading artifacts: {e}")
                self._init_fallback()
        else:
            print(f"[MLScorer] Warning: Artifacts not found at {models_dir}. Using fallback model.")
            self._init_fallback()

    def _init_fallback(self):
        # Fallback heuristic if artifacts are unavailable
        self.model = None
        self.scaler = None

    @staticmethod
    def normalize_users(count: int) -> float:
        c = max(1, count)
        norm = (np.log10(c) / 4.0) * 100.0
        return float(np.clip(norm, 0.0, 100.0))

    @staticmethod
    def normalize_systems(count: int) -> float:
        c = max(1, count)
        norm = (np.log10(c) / 2.7) * 100.0
        return float(np.clip(norm, 0.0, 100.0))

    def encode_incident_type(self, incident_type: str) -> int:
        return INCIDENT_TYPE_MAP.get(incident_type, 0)

    def encode_asset_type(self, asset_type: str) -> int:
        return ASSET_TYPE_MAP.get(asset_type, 0)

    def predict_score(self, feature_dict: Dict[str, Any]) -> float:
        """
        Takes raw or prepared feature dict with 12 features,
        scales them, and returns predicted ML priority score in [0.0, 100.0].
        """
        # Ensure all 12 features exist
        feature_vector = []
        for col in FEATURE_COLUMNS:
            val = feature_dict.get(col, 50.0)
            feature_vector.append(float(val))

        import pandas as pd
        X_df = pd.DataFrame([feature_vector], columns=FEATURE_COLUMNS)

        if self.model is not None and self.scaler is not None:
            try:
                X_scaled = self.scaler.transform(X_df)
                pred = self.model.predict(X_scaled)[0]
                return float(np.clip(pred, 0.0, 100.0))
            except Exception as e:
                print(f"[MLScorer] Prediction error: {e}, falling back to weighted baseline")

        # Robust analytical fallback formula matching training signals
        s = feature_dict.get("severity", 50.0)
        ds = feature_dict.get("data_sensitivity", 50.0)
        ai = feature_dict.get("asset_importance", 50.0)
        ac = feature_dict.get("attack_confidence", 50.0)
        un = feature_dict.get("affected_users_normalized", 30.0)
        bi = feature_dict.get("business_impact", 50.0)
        sn = feature_dict.get("affected_system_count_normalized", 20.0)
        tr = feature_dict.get("time_risk", 0.2)
        hf = feature_dict.get("historical_frequency", 0.5)
        rec = feature_dict.get("recurrence", 0)

        score = (0.24 * s + 0.20 * bi + 0.18 * ai + 0.14 * ds + 0.10 * ac + 0.08 * un + 0.06 * sn)
        score += (tr * 6.0 + hf * 4.0 + rec * 3.5)
        return float(np.clip(score, 0.0, 100.0))

    def get_feature_importances(self) -> Dict[str, float]:
        if self.evaluation_metrics and "feature_importances" in self.evaluation_metrics:
            return self.evaluation_metrics["feature_importances"]
        return {col: round(1.0 / len(FEATURE_COLUMNS), 4) for col in FEATURE_COLUMNS}

ml_scorer = MLScorer()
