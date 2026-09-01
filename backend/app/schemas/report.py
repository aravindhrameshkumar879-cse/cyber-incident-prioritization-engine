from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class ReportCreateRequest(BaseModel):
    incident_id: int
    report_type: str = "executive"
    include_mitigations: bool = True

class ReportResponse(BaseModel):
    id: int
    report_code: str
    incident_id: int
    title: str
    report_type: str
    file_path: str
    download_url: str
    generated_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AnalyticsSummaryResponse(BaseModel):
    total_incidents: int
    active_incidents: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    mean_ml_score: float
    mean_priority_score: float
    type_distribution: List[Dict[str, Any]]
    severity_distribution: List[Dict[str, Any]]
    top_affected_assets: List[Dict[str, Any]]
    status_distribution: List[Dict[str, Any]]
    recent_trend: List[Dict[str, Any]]
