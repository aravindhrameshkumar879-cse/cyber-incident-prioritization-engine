import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.session import engine, Base, SessionLocal
from app.models.user import User
from app.models.asset import Asset
from app.models.incident import Incident
from app.models.report import Report
from app.core.security import get_password_hash

# Routers
from app.api.auth import router as auth_router
from app.api.incidents import router as incidents_router
from app.api.simulator import router as simulator_router
from app.api.analytics import router as analytics_router
from app.api.reports import router as reports_router
from app.api.model import router as model_router
from app.api.demo import router as demo_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Ensure DB tables
    Base.metadata.create_all(bind=engine)

    # 2. Seed Default Admin User if absent
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if not admin_user:
            admin_user = User(
                email=settings.ADMIN_EMAIL,
                full_name=settings.ADMIN_NAME,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print(f"[Startup] Seeded Admin User: {settings.ADMIN_EMAIL}")
    finally:
        db.close()

    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Next-Generation Hybrid ML + Rule-Based Incident Prioritization with Explainable AI & Comparative Reasoning",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(incidents_router, prefix=settings.API_V1_STR)
app.include_router(simulator_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(model_router, prefix=settings.API_V1_STR)
app.include_router(demo_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "engine": "Cyber Incident Prioritization Engine",
        "status": "operational",
        "docs": "/api/docs",
        "hybrid_formula": "S = 0.65 * S_ML + 0.35 * S_Rule",
        "version": "1.0.0"
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "prioritization-engine"}
