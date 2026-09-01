from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from collections import defaultdict
from app.db.session import get_db
from app.models.incident import Incident
from app.schemas.report import AnalyticsSummaryResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(db: Session = Depends(get_db)):
    incidents = db.query(Incident).all()

    total = len(incidents)
    active = sum(1 for i in incidents if i.status in ["new", "investigating"])
    
    crit = sum(1 for i in incidents if i.priority_level == "CRITICAL")
    high = sum(1 for i in incidents if i.priority_level == "HIGH")
    med = sum(1 for i in incidents if i.priority_level == "MEDIUM")
    low = sum(1 for i in incidents if i.priority_level == "LOW")

    mean_ml = float(sum(i.ml_score for i in incidents) / total) if total > 0 else 0.0
    mean_p = float(sum(i.priority_score for i in incidents) / total) if total > 0 else 0.0

    # Type distribution
    type_counts = defaultdict(lambda: {"count": 0, "total_score": 0.0})
    for i in incidents:
        type_counts[i.incident_type]["count"] += 1
        type_counts[i.incident_type]["total_score"] += i.priority_score

    type_dist = [
        {
            "name": t,
            "count": data["count"],
            "avg_score": round(data["total_score"] / data["count"], 1) if data["count"] > 0 else 0.0
        }
        for t, data in type_counts.items()
    ]
    type_dist.sort(key=lambda x: x["count"], reverse=True)

    # Severity buckets
    sev_buckets = {"0-25": 0, "26-50": 0, "51-75": 0, "76-100": 0}
    for i in incidents:
        if i.severity <= 25:
            sev_buckets["0-25"] += 1
        elif i.severity <= 50:
            sev_buckets["26-50"] += 1
        elif i.severity <= 75:
            sev_buckets["51-75"] += 1
        else:
            sev_buckets["76-100"] += 1

    sev_dist = [{"range": k, "count": v} for k, v in sev_buckets.items()]

    # Top affected assets
    asset_counts = defaultdict(lambda: {"count": 0, "max_score": 0.0, "asset_type": ""})
    for i in incidents:
        asset_counts[i.asset_name]["count"] += 1
        asset_counts[i.asset_name]["asset_type"] = i.asset_type
        if i.priority_score > asset_counts[i.asset_name]["max_score"]:
            asset_counts[i.asset_name]["max_score"] = i.priority_score

    top_assets = [
        {
            "asset_name": name,
            "asset_type": data["asset_type"],
            "incident_count": data["count"],
            "max_priority": round(data["max_score"], 1)
        }
        for name, data in asset_counts.items()
    ]
    top_assets.sort(key=lambda x: x["incident_count"], reverse=True)
    top_assets = top_assets[:8]

    # Status distribution
    status_counts = defaultdict(int)
    for i in incidents:
        status_counts[i.status] += 1
    status_dist = [{"status": k, "count": v} for k, v in status_counts.items()]

    # Trend by detected date (day)
    trend_counts = defaultdict(lambda: {"critical": 0, "high": 0, "medium": 0, "low": 0})
    for i in incidents:
        day_str = i.detected_at.strftime("%b %d") if i.detected_at else "Today"
        lvl = i.priority_level.lower()
        if lvl in trend_counts[day_str]:
            trend_counts[day_str][lvl] += 1

    recent_trend = [
        {
            "date": day,
            "critical": data["critical"],
            "high": data["high"],
            "medium": data["medium"],
            "low": data["low"],
            "total": data["critical"] + data["high"] + data["medium"] + data["low"]
        }
        for day, data in list(trend_counts.items())[-7:]
    ]

    return AnalyticsSummaryResponse(
        total_incidents=total,
        active_incidents=active,
        critical_count=crit,
        high_count=high,
        medium_count=med,
        low_count=low,
        mean_ml_score=round(mean_ml, 2),
        mean_priority_score=round(mean_p, 2),
        type_distribution=type_dist,
        severity_distribution=sev_dist,
        top_affected_assets=top_assets,
        status_distribution=status_dist,
        recent_trend=recent_trend
    )
