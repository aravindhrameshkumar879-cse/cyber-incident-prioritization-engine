from datetime import datetime, timezone
import json
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from app.db.session import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_code = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    incident_type = Column(String(100), nullable=False)  # e.g., 'Ransomware', 'Data Exfiltration'
    status = Column(String(50), default="new", index=True)  # 'new', 'investigating', 'contained', 'resolved'

    # Target Asset
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    asset_name = Column(String(255), nullable=False)
    asset_type = Column(String(100), nullable=False)

    # 12 Core Contextual Features
    severity = Column(Float, nullable=False, default=50.0)
    data_sensitivity = Column(Float, nullable=False, default=50.0)
    asset_importance = Column(Float, nullable=False, default=50.0)
    attack_confidence = Column(Float, nullable=False, default=50.0)
    
    raw_users = Column(Integer, default=1)
    affected_users_normalized = Column(Float, nullable=False, default=0.0)
    
    business_impact = Column(Float, nullable=False, default=50.0)
    incident_type_encoded = Column(Integer, default=0)
    asset_type_encoded = Column(Integer, default=0)
    time_risk = Column(Float, nullable=False, default=0.2)
    historical_frequency = Column(Float, nullable=False, default=0.5)
    recurrence = Column(Integer, default=0)
    
    raw_systems = Column(Integer, default=1)
    affected_system_count_normalized = Column(Float, nullable=False, default=0.0)

    # Scoring Results
    ml_score = Column(Float, nullable=False, default=0.0)
    rule_score = Column(Float, nullable=False, default=0.0)
    priority_score = Column(Float, nullable=False, default=0.0, index=True)
    priority_level = Column(String(50), default="LOW", index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    priority_rank = Column(Integer, default=0, index=True)

    # Explainability metadata
    why_number_one = Column(Text, nullable=True)
    factor_contributions_json = Column(Text, nullable=True)  # Serialized dict of factor deltas/weights
    mitigation_recommendations_json = Column(Text, nullable=True)

    # Ownership & Timestamps
    assigned_to = Column(String(255), nullable=True)
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @property
    def factor_contributions(self):
        if self.factor_contributions_json:
            try:
                return json.loads(self.factor_contributions_json)
            except Exception:
                return {}
        return {}

    @property
    def mitigation_recommendations(self):
        if self.mitigation_recommendations_json:
            try:
                return json.loads(self.mitigation_recommendations_json)
            except Exception:
                return []
        return []
