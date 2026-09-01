import pytest
import os
import sys

# Ensure backend and ml are in sys.path
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(WORKSPACE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

from app.engine.ml_scorer import ml_scorer
from app.engine.rule_engine import rule_engine
from app.engine.hybrid_prioritizer import hybrid_prioritizer, classify_priority_level
from app.engine.explainability import explainability_engine

def test_ml_scorer_prediction_bounds():
    factors = {
        "severity": 95.0,
        "data_sensitivity": 90.0,
        "asset_importance": 98.0,
        "attack_confidence": 95.0,
        "affected_users_normalized": 80.0,
        "business_impact": 92.0,
        "incident_type_encoded": 0,
        "asset_type_encoded": 0,
        "time_risk": 0.9,
        "historical_frequency": 0.8,
        "recurrence": 1,
        "affected_system_count_normalized": 70.0
    }
    score = ml_scorer.predict_score(factors)
    assert 0.0 <= score <= 100.0
    assert score >= 75.0, "Critical factors should yield high ML score"

def test_rule_engine_critical_boosts():
    factors = {
        "severity": 90.0,
        "data_sensitivity": 85.0,
        "business_impact": 88.0,
        "asset_importance": 95.0,
        "asset_type": "Domain Controller",
        "incident_type": "Ransomware",
        "time_risk": 0.75,
        "recurrence": 1,
        "raw_systems": 55,
        "attack_confidence": 90.0
    }
    rule_score, applied_rules = rule_engine.evaluate(factors)
    assert 0.0 <= rule_score <= 100.0
    assert rule_score >= 80.0
    rule_names = [r["rule"] for r in applied_rules]
    assert "Tier-0 Critical Asset Rule" in rule_names
    assert "Crown-Jewel Infrastructure Target" in rule_names
    assert "Critical Threat Vector Rule" in rule_names
    assert "Off-Hours & Weekend Multiplier" in rule_names
    assert "Persistent Campaign / Recurrence Flag" in rule_names
    assert "Massive Blast Radius Rule" in rule_names

def test_hybrid_combination_and_thresholds():
    factors = {
        "severity": 85.0,
        "data_sensitivity": 80.0,
        "asset_importance": 90.0,
        "attack_confidence": 85.0,
        "raw_users": 500,
        "business_impact": 85.0,
        "incident_type": "Ransomware",
        "asset_type": "Payment Gateway",
        "time_risk": 0.7,
        "historical_frequency": 0.5,
        "recurrence": 1,
        "raw_systems": 12
    }
    p_score, ml_score, rule_score, p_level, applied_rules = hybrid_prioritizer.calculate_priority(factors)
    expected_hybrid = round(0.65 * ml_score + 0.35 * rule_score, 2)
    assert abs(p_score - expected_hybrid) < 0.05
    assert p_level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

def test_deterministic_tie_breaking_order():
    item_a = {
        "priority_score": 85.0,
        "business_impact": 80.0,
        "asset_importance": 90.0,
        "attack_confidence": 85.0,
        "detected_at": "2026-09-01T10:00:00Z"
    }
    item_b = {
        "priority_score": 85.0,
        "business_impact": 75.0,  # Lower biz impact should rank lower
        "asset_importance": 90.0,
        "attack_confidence": 85.0,
        "detected_at": "2026-09-01T09:00:00Z"
    }
    key_a = hybrid_prioritizer.tie_break_key(item_a)
    key_b = hybrid_prioritizer.tie_break_key(item_b)
    # Lower tuple means higher rank in Python sorted()
    assert key_a < key_b, "Item A should rank higher than Item B due to higher business impact"

def test_comparative_reasoning():
    inc_a = {
        "incident_code": "INC-001",
        "title": "Ransomware on DC",
        "incident_type": "Ransomware",
        "asset_type": "Domain Controller",
        "priority_score": 92.5,
        "ml_score": 90.0,
        "rule_score": 97.0,
        "severity": 95.0,
        "asset_importance": 98.0,
        "business_impact": 94.0,
        "attack_confidence": 92.0,
        "data_sensitivity": 90.0,
        "raw_users": 2000,
        "raw_systems": 30,
        "time_risk": 0.8,
        "recurrence": 1
    }
    inc_b = {
        "incident_code": "INC-002",
        "title": "Phishing on Workstation",
        "incident_type": "Phishing",
        "asset_type": "Workstation",
        "priority_score": 45.0,
        "ml_score": 48.0,
        "rule_score": 40.0,
        "severity": 50.0,
        "asset_importance": 40.0,
        "business_impact": 42.0,
        "attack_confidence": 75.0,
        "data_sensitivity": 40.0,
        "raw_users": 15,
        "raw_systems": 1,
        "time_risk": 0.2,
        "recurrence": 0
    }
    comparison = explainability_engine.compare_incidents(inc_a, inc_b)
    assert comparison["higher_priority_code"] == "INC-001"
    assert comparison["score_difference"] == 47.5
    assert len(comparison["divergent_factors"]) > 0
    assert "INC-001 is prioritized over INC-002" in comparison["plain_language_justification"]
