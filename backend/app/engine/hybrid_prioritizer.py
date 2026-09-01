from typing import Dict, Any, Tuple, List
from datetime import datetime
from app.engine.ml_scorer import ml_scorer
from app.engine.rule_engine import rule_engine

ML_WEIGHT = 0.65
RULE_WEIGHT = 0.35

def classify_priority_level(score: float) -> str:
    if score >= 80.0:
        return "CRITICAL"
    elif score >= 60.0:
        return "HIGH"
    elif score >= 30.0:
        return "MEDIUM"
    else:
        return "LOW"

class HybridPrioritizer:
    @staticmethod
    def calculate_priority(factors: Dict[str, Any]) -> Tuple[float, float, float, str, List[Dict[str, Any]]]:
        """
        Calculates ML Score (65%), Rule Score (35%), and Hybrid Final Priority Score.
        Returns (priority_score, ml_score, rule_score, priority_level, applied_rules).
        """
        # Ensure log-normalized user count & system count exist
        raw_users = int(factors.get("raw_users", 1))
        if "affected_users_normalized" not in factors or factors["affected_users_normalized"] is None:
            factors["affected_users_normalized"] = ml_scorer.normalize_users(raw_users)

        raw_systems = int(factors.get("raw_systems", 1))
        if "affected_system_count_normalized" not in factors or factors["affected_system_count_normalized"] is None:
            factors["affected_system_count_normalized"] = ml_scorer.normalize_systems(raw_systems)

        # Encodings
        if "incident_type_encoded" not in factors:
            factors["incident_type_encoded"] = ml_scorer.encode_incident_type(factors.get("incident_type", ""))
        if "asset_type_encoded" not in factors:
            factors["asset_type_encoded"] = ml_scorer.encode_asset_type(factors.get("asset_type", ""))

        # Business impact fallback
        if factors.get("business_impact") is None:
            s = float(factors.get("severity", 50.0))
            ds = float(factors.get("data_sensitivity", 50.0))
            ai = float(factors.get("asset_importance", 50.0))
            factors["business_impact"] = round(0.35 * s + 0.35 * ds + 0.30 * ai, 2)

        # 1. ML Score (65%)
        ml_score = ml_scorer.predict_score(factors)

        # 2. Rule Engine Score (35%)
        rule_score, applied_rules = rule_engine.evaluate(factors)

        # 3. Hybrid Combination
        priority_score = (ML_WEIGHT * ml_score) + (RULE_WEIGHT * rule_score)
        priority_score = round(float(priority_score), 2)
        priority_level = classify_priority_level(priority_score)

        return priority_score, round(ml_score, 2), round(rule_score, 2), priority_level, applied_rules

    @staticmethod
    def tie_break_key(item: Any):
        """
        Deterministic tie-breaking comparator key:
        1. priority_score (Descending: -score)
        2. business_impact (Descending: -impact)
        3. asset_importance (Descending: -importance)
        4. attack_confidence (Descending: -confidence)
        5. detected_at (Ascending: oldest uncontained first)
        """
        if isinstance(item, dict):
            p_score = float(item.get("priority_score", 0.0))
            biz_imp = float(item.get("business_impact", 0.0))
            asset_imp = float(item.get("asset_importance", 0.0))
            attack_conf = float(item.get("attack_confidence", 0.0))
            det_at = item.get("detected_at")
        else:
            p_score = float(getattr(item, "priority_score", 0.0))
            biz_imp = float(getattr(item, "business_impact", 0.0))
            asset_imp = float(getattr(item, "asset_importance", 0.0))
            attack_conf = float(getattr(item, "attack_confidence", 0.0))
            det_at = getattr(item, "detected_at", None)

        if isinstance(det_at, datetime):
            timestamp = det_at.timestamp()
        elif isinstance(det_at, str):
            try:
                timestamp = datetime.fromisoformat(det_at.replace("Z", "+00:00")).timestamp()
            except Exception:
                timestamp = 0.0
        else:
            timestamp = 0.0

        return (-p_score, -biz_imp, -asset_imp, -attack_conf, timestamp)

hybrid_prioritizer = HybridPrioritizer()
