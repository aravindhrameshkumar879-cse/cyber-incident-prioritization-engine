"""
Synthetic Cyber Incident Dataset Generator
Generates 55,000+ realistic cyber incident triage scenarios with multi-dimensional risk factors.
"""

import numpy as np
import pandas as pd
import json
import os

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

INCIDENT_TYPE_WEIGHTS = {
    "Ransomware": 1.35,
    "Data Exfiltration": 1.30,
    "Privilege Escalation": 1.20,
    "Unauthorized Access": 1.15,
    "Insider Threat": 1.10,
    "DDoS": 0.95,
    "Malware": 0.85,
    "Phishing": 0.75,
}

ASSET_TYPE_WEIGHTS = {
    "Domain Controller": 1.30,
    "Payment Gateway": 1.25,
    "Database Server": 1.20,
    "VPN Gateway": 1.10,
    "Cloud Storage": 1.05,
    "Application Server": 0.95,
    "Workstation": 0.75,
    "Internal Wiki": 0.65,
}


def generate_dataset(num_samples: int = 55000, random_state: int = 42) -> pd.DataFrame:
    np.random.seed(random_state)

    # 1. Technical Alert Severity (0 - 100)
    severity = np.clip(np.random.beta(a=3, b=3, size=num_samples) * 100, 5, 100)

    # 2. Data Sensitivity (0 - 100)
    data_sensitivity = np.clip(np.random.beta(a=2.5, b=2.5, size=num_samples) * 100, 0, 100)

    # 3. Asset Importance (0 - 100)
    asset_importance = np.clip(np.random.beta(a=3, b=2.8, size=num_samples) * 100, 10, 100)

    # 4. Attack Confidence (0 - 100)
    attack_confidence = np.clip(np.random.beta(a=4, b=2, size=num_samples) * 100, 15, 100)

    # 5. Affected Users raw count -> log-scaled normalized (0 - 100)
    raw_users = np.random.exponential(scale=150, size=num_samples) + 1
    raw_users = np.clip(raw_users, 1, 10000)
    # log10(1) = 0, log10(10000) = 4
    affected_users_normalized = np.clip((np.log10(raw_users) / 4.0) * 100, 0, 100)

    # 6. Business Impact (0 - 100)
    # Strongly driven by severity, data sensitivity, and asset importance with variance
    base_biz = (0.35 * severity + 0.35 * data_sensitivity + 0.30 * asset_importance)
    business_impact = np.clip(base_biz + np.random.normal(0, 8, num_samples), 0, 100)

    # 7. Incident Type & Categorical Encoding
    incident_types = np.random.choice(
        INCIDENT_TYPES,
        size=num_samples,
        p=[0.12, 0.14, 0.15, 0.10, 0.18, 0.15, 0.08, 0.08]
    )
    incident_type_map = {name: idx for idx, name in enumerate(INCIDENT_TYPES)}
    incident_type_encoded = np.array([incident_type_map[t] for t in incident_types])

    # 8. Asset Type & Categorical Encoding
    asset_types = np.random.choice(
        ASSET_TYPES,
        size=num_samples,
        p=[0.10, 0.16, 0.10, 0.14, 0.20, 0.18, 0.06, 0.06]
    )
    asset_type_map = {name: idx for idx, name in enumerate(ASSET_TYPES)}
    asset_type_encoded = np.array([asset_type_map[a] for a in asset_types])

    # 9. Time Risk (0.0 to 1.0) - off hours, weekends
    # 0.2 baseline during working hours, up to 1.0 for late night weekend
    time_risk = np.clip(np.random.beta(a=2, b=4, size=num_samples) * 1.2, 0.05, 1.0)

    # 10. Historical Frequency (0.0 to 1.0) - rarity factor (1.0 = rare zero-day, 0.1 = noisy common)
    historical_frequency = np.clip(np.random.beta(a=2, b=3, size=num_samples), 0.02, 1.0)

    # 11. Recurrence (0 or 1)
    recurrence = np.random.binomial(n=1, p=0.28, size=num_samples)

    # 12. Affected System Count normalized (0 - 100)
    raw_systems = np.random.exponential(scale=15, size=num_samples) + 1
    raw_systems = np.clip(raw_systems, 1, 500)
    affected_system_count_normalized = np.clip((np.log10(raw_systems) / 2.7) * 100, 0, 100)

    # Calculate Ground-Truth ML Priority Target (0 - 100)
    # Combines technical, impact, asset, and temporal factors with slight non-linear interactions
    type_mult = np.array([INCIDENT_TYPE_WEIGHTS[t] for t in incident_types])
    asset_mult = np.array([ASSET_TYPE_WEIGHTS[a] for a in asset_types])

    core_signal = (
        0.24 * severity +
        0.20 * business_impact +
        0.18 * asset_importance +
        0.14 * data_sensitivity +
        0.10 * attack_confidence +
        0.08 * affected_users_normalized +
        0.06 * affected_system_count_normalized
    )

    # Factor multipliers and additions
    multiplier = 0.85 + (type_mult - 1.0) * 0.25 + (asset_mult - 1.0) * 0.20
    temporal_boost = time_risk * 6.0 + historical_frequency * 4.0 + recurrence * 3.5

    target_score = (core_signal * multiplier) + temporal_boost + np.random.normal(0, 3.0, num_samples)
    target_score = np.clip(target_score, 0.0, 100.0)

    df = pd.DataFrame({
        "severity": np.round(severity, 2),
        "data_sensitivity": np.round(data_sensitivity, 2),
        "asset_importance": np.round(asset_importance, 2),
        "attack_confidence": np.round(attack_confidence, 2),
        "affected_users_normalized": np.round(affected_users_normalized, 2),
        "business_impact": np.round(business_impact, 2),
        "incident_type_encoded": incident_type_encoded,
        "asset_type_encoded": asset_type_encoded,
        "time_risk": np.round(time_risk, 3),
        "historical_frequency": np.round(historical_frequency, 3),
        "recurrence": recurrence,
        "affected_system_count_normalized": np.round(affected_system_count_normalized, 2),
        "priority_target": np.round(target_score, 2),
        # Informational columns for reference
        "incident_type_name": incident_types,
        "asset_type_name": asset_types,
        "raw_users": np.round(raw_users).astype(int),
        "raw_systems": np.round(raw_systems).astype(int),
    })

    return df


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "synthetic_incidents.csv")
    print(f"Generating 55,000 synthetic incident records...")
    df = generate_dataset(55000)
    df.to_csv(csv_path, index=False)
    print(f"Saved synthetic dataset to: {csv_path} (Shape: {df.shape})")
