import os

class Settings:
    PROJECT_NAME: str = "Cyber Incident Prioritization Engine"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "soc_prioritization_engine_super_secret_jwt_key_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Path resolution
    CORE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR = os.path.dirname(CORE_DIR)
    BACKEND_DIR = os.path.dirname(APP_DIR)
    WORKSPACE_DIR = os.path.dirname(BACKEND_DIR)

    # Serverless / Vercel detection: Vercel filesystems are read-only except /tmp
    IS_VERCEL: bool = os.getenv("VERCEL") == "1" or os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None

    if IS_VERCEL:
        DEFAULT_DB_PATH = "/tmp/cyber_soc.db"
    else:
        try:
            test_file = os.path.join(BACKEND_DIR, ".write_test")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            DEFAULT_DB_PATH = os.path.join(BACKEND_DIR, "cyber_soc.db")
        except Exception:
            DEFAULT_DB_PATH = "/tmp/cyber_soc.db"

    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")
    
    # ML Artifacts directory: check app/ml/models, backend/ml/models, workspace/ml/models
    _app_ml = os.path.join(APP_DIR, "ml", "models")
    _backend_ml = os.path.join(BACKEND_DIR, "ml", "models")
    _workspace_ml = os.path.join(WORKSPACE_DIR, "ml", "models")

    if os.path.exists(_app_ml) and os.path.exists(os.path.join(_app_ml, "priority_model.pkl")):
        _chosen_ml = _app_ml
    elif os.path.exists(_backend_ml) and os.path.exists(os.path.join(_backend_ml, "priority_model.pkl")):
        _chosen_ml = _backend_ml
    elif os.path.exists(_workspace_ml) and os.path.exists(os.path.join(_workspace_ml, "priority_model.pkl")):
        _chosen_ml = _workspace_ml
    else:
        _chosen_ml = _app_ml

    ML_MODELS_DIR: str = os.getenv("ML_MODELS_DIR", _chosen_ml)
    
    # Admin Seed Credentials
    ADMIN_EMAIL: str = "admin@soc.local"
    ADMIN_PASSWORD: str = "Admin@1234"
    ADMIN_NAME: str = "Lead SOC Commander"

settings = Settings()
