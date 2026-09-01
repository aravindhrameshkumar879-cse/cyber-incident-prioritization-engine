import os
import io
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from app.core.config import settings

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        # Header
        self.drawString(54, 750, "CYBER INCIDENT PRIORITIZATION ENGINE | SOC TRIAGE DOSSIER")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 744, 558, 744)
        
        # Footer
        self.line(54, 45, 558, 45)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_text)
        self.drawString(54, 32, "CONFIDENTIAL // RESTRICTED SECURITY OPERATIONS // GENERATED VIA REPORTLAB")
        self.restoreState()


class PDFReportGenerator:
    STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports_storage")

    @classmethod
    def ensure_storage(cls):
        os.makedirs(cls.STORAGE_DIR, exist_ok=True)

    @classmethod
    def generate_incident_report(cls, incident: Any, report_type: str = "executive", generated_by: str = "Lead Analyst") -> str:
        cls.ensure_storage()
        filename = f"report_{incident.incident_code}_{report_type}_{int(datetime.now().timestamp())}.pdf"
        filepath = os.path.join(cls.STORAGE_DIR, filename)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=64,
            bottomMargin=54
        )

        styles = getSampleStyleSheet()
        
        # Custom typography styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#475569"),
            spaceAfter=12
        )
        section_heading = ParagraphStyle(
            'SectionHead',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor("#334155")
        )
        callout_style = ParagraphStyle(
            'Callout',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#0f172a")
        )

        elements = []

        # Header Title
        elements.append(Paragraph(f"Security Incident Triage Dossier: {incident.incident_code}", title_style))
        report_label = "EXECUTIVE BRIEFING & RISK ASSESSMENT" if report_type == "executive" else "TECHNICAL FORENSIC & TRIAGE REPORT"
        elements.append(Paragraph(f"{report_label} &bull; Generated on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} by {generated_by}", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"), spaceAfter=12))

        # Priority Banner Box
        level_colors = {
            "CRITICAL": colors.HexColor("#ef4444"),
            "HIGH": colors.HexColor("#f97316"),
            "MEDIUM": colors.HexColor("#eab308"),
            "LOW": colors.HexColor("#22c55e")
        }
        badge_bg = level_colors.get(incident.priority_level, colors.HexColor("#64748b"))

        banner_data = [
            [
                Paragraph(f"<b>PRIORITY RANK: #{incident.priority_rank}</b>", ParagraphStyle('RankP', fontName='Helvetica-Bold', fontSize=14, textColor=colors.white)),
                Paragraph(f"<b>HYBRID RISK SCORE: {incident.priority_score:.1f} / 100</b>", ParagraphStyle('ScoreP', fontName='Helvetica-Bold', fontSize=14, textColor=colors.white)),
                Paragraph(f"<b>LEVEL: {incident.priority_level}</b>", ParagraphStyle('LvlP', fontName='Helvetica-Bold', fontSize=14, textColor=colors.white, alignment=2))
            ]
        ]
        banner_table = Table(banner_data, colWidths=[160, 200, 144])
        banner_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), badge_bg),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(banner_table)
        elements.append(Spacer(1, 10))

        # Model Split Breakdown Table
        split_data = [
            [
                Paragraph("<b>Component</b>", body_style),
                Paragraph("<b>Weight</b>", body_style),
                Paragraph("<b>Component Score</b>", body_style),
                Paragraph("<b>Weighted Contribution</b>", body_style)
            ],
            [
                Paragraph("Machine Learning Predictive Model", body_style),
                Paragraph("65%", body_style),
                Paragraph(f"{incident.ml_score:.1f} / 100", body_style),
                Paragraph(f"{(0.65 * incident.ml_score):.2f} pts", body_style)
            ],
            [
                Paragraph("Context-Aware Deterministic Rule Engine", body_style),
                Paragraph("35%", body_style),
                Paragraph(f"{incident.rule_score:.1f} / 100", body_style),
                Paragraph(f"{(0.35 * incident.rule_score):.2f} pts", body_style)
            ],
            [
                Paragraph("<b>Final Prioritization Score (Hybrid)</b>", body_style),
                Paragraph("<b>100%</b>", body_style),
                Paragraph(f"<b>{incident.priority_score:.1f} / 100</b>", body_style),
                Paragraph(f"<b>{incident.priority_score:.2f} pts</b>", body_style)
            ]
        ]
        split_table = Table(split_data, colWidths=[190, 80, 114, 120])
        split_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor("#f8fafc")]),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(split_table)
        elements.append(Spacer(1, 12))

        # Explainability Rationale Box
        elements.append(Paragraph("Executive Explainability & Prioritization Rationale", section_heading))
        why_text = incident.why_number_one if incident.why_number_one else (
            f"Incident {incident.incident_code} exhibits elevated threat severity ({incident.severity:.1f}/100) targeting "
            f"mission-critical {incident.asset_type} '{incident.asset_name}'. Hybrid scoring placed this at Priority {incident.priority_level}."
        )
        callout_data = [[Paragraph(why_text, callout_style)]]
        callout_table = Table(callout_data, colWidths=[504])
        callout_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fdf4" if incident.priority_level == "LOW" else ("#fef2f2" if incident.priority_level == "CRITICAL" else "#fefce8"))),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#bbf7d0" if incident.priority_level == "LOW" else ("#fecaca" if incident.priority_level == "CRITICAL" else "#fde047"))),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(callout_table)
        elements.append(Spacer(1, 12))

        # Contextual Feature Dimensions Table
        elements.append(Paragraph("Contextual Risk Factors (12 Pipeline Dimensions)", section_heading))
        factors_data = [
            [
                Paragraph("<b>Factor</b>", body_style),
                Paragraph("<b>Value</b>", body_style),
                Paragraph("<b>Factor</b>", body_style),
                Paragraph("<b>Value</b>", body_style)
            ],
            [
                Paragraph("Threat Category", body_style),
                Paragraph(str(incident.incident_type), body_style),
                Paragraph("Target Infrastructure", body_style),
                Paragraph(f"{incident.asset_name} ({incident.asset_type})", body_style)
            ],
            [
                Paragraph("Technical Alert Severity", body_style),
                Paragraph(f"{incident.severity:.1f} / 100", body_style),
                Paragraph("Data Sensitivity Index", body_style),
                Paragraph(f"{incident.data_sensitivity:.1f} / 100", body_style)
            ],
            [
                Paragraph("Asset Importance", body_style),
                Paragraph(f"{incident.asset_importance:.1f} / 100", body_style),
                Paragraph("Evaluated Business Impact", body_style),
                Paragraph(f"{incident.business_impact:.1f} / 100", body_style)
            ],
            [
                Paragraph("Attack Confidence", body_style),
                Paragraph(f"{incident.attack_confidence:.1f}%", body_style),
                Paragraph("Impacted Users", body_style),
                Paragraph(f"{incident.raw_users:,} accounts", body_style)
            ],
            [
                Paragraph("Infected Systems / Blast Radius", body_style),
                Paragraph(f"{incident.raw_systems:,} endpoints", body_style),
                Paragraph("Temporal Window Risk", body_style),
                Paragraph(f"{incident.time_risk:.2f} ({'Off-Hours' if incident.time_risk >= 0.6 else 'Standard'})", body_style)
            ],
            [
                Paragraph("Historical Recurrence Flag", body_style),
                Paragraph(f"{'Yes (Repeat Vulnerability)' if incident.recurrence == 1 else 'No (Novel / Initial)'}", body_style),
                Paragraph("Signature Frequency", body_style),
                Paragraph(f"{incident.historical_frequency:.2f} (Rarity Index)", body_style)
            ]
        ]
        factors_table = Table(factors_data, colWidths=[130, 122, 130, 122])
        factors_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(factors_table)
        elements.append(Spacer(1, 14))

        # Actionable Mitigation Checklist
        elements.append(Paragraph("Actionable SOC Containment & Remediation Checklist", section_heading))
        mitigations = incident.mitigation_recommendations or [
            "Verify perimeter egress filtering and quarantine suspicious IP endpoints.",
            "Enforce immediate credential reset for impacted service accounts.",
            "Deploy endpoint response agent to preserve forensic memory snapshot."
        ]
        
        mitig_data = []
        for idx, step in enumerate(mitigations, 1):
            mitig_data.append([
                Paragraph(f"<b>[&nbsp;&nbsp;] Step {idx}</b>", body_style),
                Paragraph(step, body_style)
            ])

        mitig_table = Table(mitig_data, colWidths=[80, 424])
        mitig_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(mitig_table)
        elements.append(Spacer(1, 16))

        # Signoff block
        signoff_data = [
            [
                Paragraph("<b>Assigned Triage Lead:</b>", body_style),
                Paragraph(incident.assigned_to or "Unassigned (Queue Lead)", body_style),
                Paragraph("<b>Audit Clearance:</b>", body_style),
                Paragraph("VERIFIED AUTOMATED DOSSIER", body_style)
            ],
            [
                Paragraph("<b>Current Status:</b>", body_style),
                Paragraph(incident.status.upper(), body_style),
                Paragraph("<b>Classification:</b>", body_style),
                Paragraph("TLP:AMBER+STRICT", body_style)
            ]
        ]
        signoff_table = Table(signoff_data, colWidths=[126, 126, 126, 126])
        signoff_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(signoff_table)

        doc.build(elements, canvasmaker=NumberedCanvas)
        return filepath

pdf_generator = PDFReportGenerator()
