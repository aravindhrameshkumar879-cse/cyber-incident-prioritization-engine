from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class SimulationRequest(BaseModel):
    incident_id: Optional[int] = None
    title: Optional[str] = "Simulation Scenario"
    incident_type: str = "Ransomware"
    asset_name: str = "Critical Host"
    asset_type: str = "Domain Controller"
    severity: float = Field(50.0, ge=0, le=100)
    data_sensitivity: float = Field(50.0, ge=0, le=100)
    asset_importance: float = Field(50.0, ge=0, le=100)
    attack_confidence: float = Field(50.0, ge=0, le=100)
    raw_users: int = Field(10, ge=1)
    business_impact: Optional[float] = None
    time_risk: float = Field(0.2, ge=0, le=1.0)
    historical_frequency: float = Field(0.5, ge=0, le=1.0)
    recurrence: int = Field(0, ge=0, le=1)
    raw_systems: int = Field(1, ge=1)

class SimulationResponse(BaseModel):
    simulated_priority_score: float
    simulated_priority_level: str
    ml_score: float
    rule_score: float
    estimated_rank_shift: Optional[int] = 0
    estimated_new_rank: Optional[int] = 1
    baseline_score: Optional[float] = None
    baseline_level: Optional[str] = None
    score_delta: Optional[float] = 0.0
    factor_contributions: Dict[str, Any]
    explainability_summary: str
    mitigation_recommendations: List[str]
