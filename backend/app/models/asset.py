from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.db.session import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    ip_address = Column(String(100), nullable=False)
    asset_type = Column(String(100), nullable=False)  # e.g., 'Domain Controller', 'Payment Gateway'
    criticality = Column(Float, default=50.0)  # 0 to 100
    department = Column(String(100), default="Infrastructure")
    owner = Column(String(100), default="SecOps")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
