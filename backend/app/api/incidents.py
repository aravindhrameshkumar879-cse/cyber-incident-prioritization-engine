from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import json

from app.db.session import get_db
from app.models.incident import Incident
from app.models.asset import Asset
from app.schemas.incident import (
    IncidentCreate, IncidentUpdateStatus, IncidentResponse, IncidentComparisonResponse
)
from app.engine.hybrid_prioritizer import hybrid_prioritizer
from app.engine.ml_scorer import ml_scorer
from app.engine.explainability import explainability_engine

router = APIRouter(prefix="/incidents", tags=["Incidents"])

def recompute_queue_ranks(db: Session):
    """
    Ranks all incidents according to the 5-tier deterministic tie-breaking key:
    1. priority_score (desc)
    2. business_impact (desc)
    3. asset_importance (desc)
    4. attack_confidence (desc)
    5. detected_at (asc)
    """
    all_incidents = db.query(Incident).all()
    # Sort deterministically
    sorted_incidents = sorted(all_incidents, key=hybrid_prioritizer.tie_break_key)
    
    for rank, inc in enumerate(sorted_incidents, 1):
        inc.priority_rank = rank
        if rank == 1:
            inc.why_number_one = explainability_engine.generate_why_number_one(inc)
    db.commit()

@router.get("/ranking")
def get_ranked_incidents(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Incident)

    if status_filter and status_filter.lower() != "all":
        query = query.filter(Incident.status == status_filter.lower())

    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                Incident.incident_code.ilike(search_fmt),
                Incident.title.ilike(search_fmt),
                Incident.incident_type.ilike(search_fmt),
                Incident.asset_name.ilike(search_fmt),
            )
        )

    all_matches = query.all()
    # Sort using tie-breaking logic
    sorted_matches = sorted(all_matches, key=hybrid_prioritizer.tie_break_key)
    total_count = len(sorted_matches)
    paginated = sorted_matches[offset : offset + limit]

    # Convert to response objects
    items = []
    for inc in paginated:
        resp = IncidentResponse.model_validate(inc)
        items.append(resp)

    # Fetch top ranked incident for spotlight
    top_incident = None
    if sorted_matches:
        top_inc_model = sorted_matches[0]
        top_incident = IncidentResponse.model_validate(top_inc_model)

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "items": items,
        "top_incident": top_incident
    }

@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Ensure factor contributions and mitigations are fresh
    if not inc.factor_contributions_json:
        contributions = explainability_engine.calculate_factor_contributions(inc)
        inc.factor_contributions_json = json.dumps(contributions)
        db.commit()
    
    return IncidentResponse.model_validate(inc)

@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_incident(inc_in: IncidentCreate, db: Session = Depends(get_db)):
    # Generate sequential code e.g. INC-3891
    latest_id = db.query(Incident.id).order_by(desc(Incident.id)).first()
    next_num = (latest_id[0] + 1) if latest_id else 101
    code = f"INC-{next_num:04d}"

    # Calculate normalized features
    norm_users = ml_scorer.normalize_users(inc_in.raw_users or 1)
    norm_systems = ml_scorer.normalize_systems(inc_in.raw_systems or 1)
    type_enc = ml_scorer.encode_incident_type(inc_in.incident_type)
    asset_enc = ml_scorer.encode_asset_type(inc_in.asset_type)

    biz_impact = inc_in.business_impact
    if biz_impact is None:
        biz_impact = round(0.35 * inc_in.severity + 0.35 * inc_in.data_sensitivity + 0.30 * inc_in.asset_importance, 2)

    factors = {
        "severity": inc_in.severity,
        "data_sensitivity": inc_in.data_sensitivity,
        "asset_importance": inc_in.asset_importance,
        "attack_confidence": inc_in.attack_confidence,
        "raw_users": inc_in.raw_users or 1,
        "affected_users_normalized": norm_users,
        "business_impact": biz_impact,
        "incident_type": inc_in.incident_type,
        "asset_type": inc_in.asset_type,
        "incident_type_encoded": type_enc,
        "asset_type_encoded": asset_enc,
        "time_risk": inc_in.time_risk if inc_in.time_risk is not None else 0.2,
        "historical_frequency": inc_in.historical_frequency if inc_in.historical_frequency is not None else 0.5,
        "recurrence": inc_in.recurrence or 0,
        "raw_systems": inc_in.raw_systems or 1,
        "affected_system_count_normalized": norm_systems
    }

    # Run Hybrid Prioritizer
    p_score, ml_sc, rule_sc, p_level, applied_rules = hybrid_prioritizer.calculate_priority(factors)

    factors["priority_score"] = p_score
    contributions = explainability_engine.calculate_factor_contributions(factors)
    mitigations = explainability_engine.get_mitigation_steps(inc_in.incident_type, inc_in.severity)

    incident = Incident(
        incident_code=code,
        title=inc_in.title,
        description=inc_in.description or f"{inc_in.incident_type} alert on {inc_in.asset_name}",
        incident_type=inc_in.incident_type,
        status="new",
        asset_name=inc_in.asset_name,
        asset_type=inc_in.asset_type,
        severity=inc_in.severity,
        data_sensitivity=inc_in.data_sensitivity,
        asset_importance=inc_in.asset_importance,
        attack_confidence=inc_in.attack_confidence,
        raw_users=inc_in.raw_users or 1,
        affected_users_normalized=norm_users,
        business_impact=biz_impact,
        incident_type_encoded=type_enc,
        asset_type_encoded=asset_enc,
        time_risk=factors["time_risk"],
        historical_frequency=factors["historical_frequency"],
        recurrence=factors["recurrence"],
        raw_systems=inc_in.raw_systems or 1,
        affected_system_count_normalized=norm_systems,
        ml_score=ml_sc,
        rule_score=rule_sc,
        priority_score=p_score,
        priority_level=p_level,
        factor_contributions_json=json.dumps(contributions),
        mitigation_recommendations_json=json.dumps(mitigations),
        detected_at=datetime.now(timezone.utc)
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    # Recalculate deterministic ranks for all queue items
    recompute_queue_ranks(db)
    db.refresh(incident)

    return IncidentResponse.model_validate(incident)

@router.post("/{incident_id}/prioritize", response_model=IncidentResponse)
def prioritize_incident(incident_id: int, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    factors = {
        "severity": inc.severity,
        "data_sensitivity": inc.data_sensitivity,
        "asset_importance": inc.asset_importance,
        "attack_confidence": inc.attack_confidence,
        "raw_users": inc.raw_users,
        "affected_users_normalized": inc.affected_users_normalized,
        "business_impact": inc.business_impact,
        "incident_type": inc.incident_type,
        "asset_type": inc.asset_type,
        "incident_type_encoded": inc.incident_type_encoded,
        "asset_type_encoded": inc.asset_type_encoded,
        "time_risk": inc.time_risk,
        "historical_frequency": inc.historical_frequency,
        "recurrence": inc.recurrence,
        "raw_systems": inc.raw_systems,
        "affected_system_count_normalized": inc.affected_system_count_normalized
    }

    p_score, ml_sc, rule_sc, p_level, applied_rules = hybrid_prioritizer.calculate_priority(factors)

    inc.ml_score = ml_sc
    inc.rule_score = rule_sc
    inc.priority_score = p_score
    inc.priority_level = p_level

    factors["priority_score"] = p_score
    inc.factor_contributions_json = json.dumps(explainability_engine.calculate_factor_contributions(factors))
    inc.mitigation_recommendations_json = json.dumps(explainability_engine.get_mitigation_steps(inc.incident_type, inc.severity))

    db.commit()
    recompute_queue_ranks(db)
    db.refresh(inc)

    return IncidentResponse.model_validate(inc)

@router.patch("/{incident_id}/status", response_model=IncidentResponse)
def update_status(incident_id: int, status_update: IncidentUpdateStatus, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    valid_statuses = {"new", "investigating", "contained", "resolved"}
    if status_update.status.lower() not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {valid_statuses}")

    inc.status = status_update.status.lower()
    inc.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(inc)

    return IncidentResponse.model_validate(inc)

@router.post("/{incident_id}/compare/{other_id}", response_model=IncidentComparisonResponse)
def compare_incidents(incident_id: int, other_id: int, db: Session = Depends(get_db)):
    inc_a = db.query(Incident).filter(Incident.id == incident_id).first()
    inc_b = db.query(Incident).filter(Incident.id == other_id).first()

    if not inc_a or not inc_b:
        raise HTTPException(status_code=404, detail="One or both incidents not found for comparison")

    comp_result = explainability_engine.compare_incidents(inc_a, inc_b)

    return IncidentComparisonResponse(
        incident_a=IncidentResponse.model_validate(inc_a),
        incident_b=IncidentResponse.model_validate(inc_b),
        higher_priority_code=comp_result["higher_priority_code"],
        score_difference=comp_result["score_difference"],
        plain_language_justification=comp_result["plain_language_justification"],
        divergent_factors=comp_result["divergent_factors"],
        ml_delta=comp_result["ml_delta"],
        rule_delta=comp_result["rule_delta"]
    )
