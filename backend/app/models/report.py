from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from app.db.session import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_code = Column(String(50), unique=True, index=True, nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    title = Column(String(255), nullable=False)
    report_type = Column(String(50), default="executive")  # 'executive', 'technical', 'comprehensive'
    summary = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=False)
    generated_by = Column(String(255), default="System")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
