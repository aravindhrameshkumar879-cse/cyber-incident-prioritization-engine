import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.report import Report
from app.models.incident import Incident
from app.schemas.report import ReportCreateRequest, ReportResponse
from app.reports.pdf_generator import pdf_generator

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("", response_model=ReportResponse)
def generate_report(req: ReportCreateRequest, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == req.incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    filepath = pdf_generator.generate_incident_report(
        incident=incident,
        report_type=req.report_type,
        generated_by="SOC Incident Commander"
    )

    code = f"REP-{int(datetime.now().timestamp())}"
    title = f"{req.report_type.capitalize()} Report: {incident.incident_code} - {incident.title}"
    
    report = Report(
        report_code=code,
        incident_id=incident.id,
        title=title,
        report_type=req.report_type,
        file_path=filepath,
        generated_by="SOC Incident Commander"
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return ReportResponse(
        id=report.id,
        report_code=report.report_code,
        incident_id=report.incident_id,
        title=report.title,
        report_type=report.report_type,
        file_path=report.file_path,
        download_url=f"/api/reports/{report.id}/download",
        generated_by=report.generated_by,
        created_at=report.created_at
    )

@router.get("/{report_id}/download")
def download_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report or not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Report file not found")

    filename = os.path.basename(report.file_path)
    return FileResponse(
        path=report.file_path,
        filename=filename,
        media_type="application/pdf"
    )

@router.get("", response_model=List[ReportResponse])
def list_reports(db: Session = Depends(get_db)):
    reports = db.query(Report).order_by(Report.created_at.desc()).limit(50).all()
    out = []
    for r in reports:
        out.append(ReportResponse(
            id=r.id,
            report_code=r.report_code,
            incident_id=r.incident_id,
            title=r.title,
            report_type=r.report_type,
            file_path=r.file_path,
            download_url=f"/api/reports/{r.id}/download",
            generated_by=r.generated_by,
            created_at=r.created_at
        ))
    return out
