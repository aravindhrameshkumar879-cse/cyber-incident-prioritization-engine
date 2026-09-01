from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class IncidentBase(BaseModel):
    title: str
    description: Optional[str] = None
    incident_type: str
    asset_name: str
    asset_type: str
    severity: float = Field(..., ge=0, le=100)
    data_sensitivity: float = Field(..., ge=0, le=100)
    asset_importance: float = Field(..., ge=0, le=100)
    attack_confidence: float = Field(..., ge=0, le=100)
    raw_users: Optional[int] = 1
    business_impact: Optional[float] = None
    time_risk: Optional[float] = 0.2
    historical_frequency: Optional[float] = 0.5
    recurrence: Optional[int] = 0
    raw_systems: Optional[int] = 1

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdateStatus(BaseModel):
    status: str  # 'new', 'investigating', 'contained', 'resolved'

class FactorContribution(BaseModel):
    name: str
    label: str
    value: float
    importance_pct: float
    contribution: float
    description: str

class IncidentResponse(BaseModel):
    id: int
    incident_code: str
    title: str
    description: Optional[str] = None
    incident_type: str
    status: str
    asset_name: str
    asset_type: str
    
    severity: float
    data_sensitivity: float
    asset_importance: float
    attack_confidence: float
    raw_users: int
    affected_users_normalized: float
    business_impact: float
    incident_type_encoded: int
    asset_type_encoded: int
    time_risk: float
    historical_frequency: float
    recurrence: int
    raw_systems: int
    affected_system_count_normalized: float

    ml_score: float
    rule_score: float
    priority_score: float
    priority_level: str
    priority_rank: int

    why_number_one: Optional[str] = None
    factor_contributions: Optional[Dict[str, Any]] = None
    mitigation_recommendations: Optional[List[str]] = None

    assigned_to: Optional[str] = None
    detected_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class IncidentComparisonResponse(BaseModel):
    incident_a: IncidentResponse
    incident_b: IncidentResponse
    higher_priority_code: str
    score_difference: float
    plain_language_justification: str
    divergent_factors: List[Dict[str, Any]]
    ml_delta: float
    rule_delta: float
