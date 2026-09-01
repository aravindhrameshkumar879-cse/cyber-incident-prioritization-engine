"""
Model Training Pipeline
Trains a calibrated regression model to predict cybersecurity incident risk scores.
Saves priority_model.pkl, scaler.pkl, feature_config.json, and evaluation_metrics.json.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import HistGradientBoostingRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dataset.generate import generate_dataset, INCIDENT_TYPES, ASSET_TYPES

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

TARGET_COLUMN = "priority_target"


def train_pipeline():
    print("Step 1: Generating/loading synthetic dataset (55,000 samples)...")
    df = generate_dataset(num_samples=55000, random_state=42)

    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].values

    # Train / Test split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples...")

    # Standard Scaler for numerical features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # HistGradientBoostingRegressor is extremely fast, highly accurate, and robust
    print("Step 2: Fitting Gradient Boosting Regressor...")
    model = HistGradientBoostingRegressor(
        max_iter=150,
        learning_rate=0.08,
        max_depth=7,
        l2_regularization=0.1,
        random_state=42
    )
    model.fit(X_train_scaled, y_train)

    # Predictions & Metrics
    y_pred = model.predict(X_test_scaled)
    y_pred = np.clip(y_pred, 0.0, 100.0)

    r2 = float(r2_score(y_test, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    mae = float(mean_absolute_error(y_test, y_pred))

    print(f"Evaluation Results:")
    print(f"  R² Score:  {r2:.4f}")
    print(f"  RMSE:      {rmse:.4f}")
    print(f"  MAE:       {mae:.4f}")

    # Estimate Feature Importances via Permutation or Linear Proxy
    # For HistGradientBoostingRegressor, compute permutation importance approximation or weights
    from sklearn.inspection import permutation_importance
    print("Step 3: Calculating feature importances...")
    perm = permutation_importance(model, X_test_scaled[:2500], y_test[:2500], n_repeats=5, random_state=42)
    importances = perm.importances_mean
    norm_importances = importances / np.sum(importances)
    feature_importances = {
        feat: round(float(imp), 4)
        for feat, imp in zip(FEATURE_COLUMNS, norm_importances)
    }

    # Prepare artifacts directory
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
    os.makedirs(models_dir, exist_ok=True)

    # Save artifacts
    model_path = os.path.join(models_dir, "priority_model.pkl")
    scaler_path = os.path.join(models_dir, "scaler.pkl")
    config_path = os.path.join(models_dir, "feature_config.json")
    metrics_path = os.path.join(models_dir, "evaluation_metrics.json")

    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    feature_config = {
        "features": FEATURE_COLUMNS,
        "incident_types": INCIDENT_TYPES,
        "asset_types": ASSET_TYPES,
        "target": TARGET_COLUMN,
        "feature_importances": feature_importances,
        "scaling_mean": scaler.mean_.tolist(),
        "scaling_scale": scaler.scale_.tolist()
    }

    with open(config_path, "w") as f:
        json.dump(feature_config, f, indent=2)

    evaluation_metrics = {
        "model_name": "HistGradientBoostingRegressor",
        "dataset_samples": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "r2_score": round(r2, 4),
        "rmse": round(rmse, 4),
        "mae": round(mae, 4),
        "feature_importances": feature_importances,
        "trained_at": pd.Timestamp.now().isoformat()
    }

    with open(metrics_path, "w") as f:
        json.dump(evaluation_metrics, f, indent=2)

    print(f"Artifacts successfully saved to {models_dir}:")
    print(f"  - {model_path}")
    print(f"  - {scaler_path}")
    print(f"  - {config_path}")
    print(f"  - {metrics_path}")


if __name__ == "__main__":
    train_pipeline()
