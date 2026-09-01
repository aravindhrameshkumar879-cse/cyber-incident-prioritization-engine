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

    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BACKEND_DIR, 'cyber_soc.db')}")
    
    # ML Artifacts directory: workspace/ml/models or fallback backend/ml/models
    _workspace_ml = os.path.join(WORKSPACE_DIR, "ml", "models")
    _backend_ml = os.path.join(BACKEND_DIR, "ml", "models")
    ML_MODELS_DIR: str = os.getenv(
        "ML_MODELS_DIR",
        _workspace_ml if os.path.exists(_workspace_ml) else _backend_ml
    )
    
    # Admin Seed Credentials
    ADMIN_EMAIL: str = "admin@soc.local"
    ADMIN_PASSWORD: str = "Admin@1234"
    ADMIN_NAME: str = "Lead SOC Commander"

settings = Settings()
