import random
import json
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.incident import Incident
from app.models.asset import Asset
from app.engine.hybrid_prioritizer import hybrid_prioritizer
from app.engine.ml_scorer import ml_scorer
from app.engine.explainability import explainability_engine

router = APIRouter(prefix="/demo", tags=["Demo"])

DEMO_ASSETS = [
    {"name": "CORP-DC-01.local", "ip_address": "10.0.1.10", "asset_type": "Domain Controller", "criticality": 98.0, "department": "Identity & Security"},
    {"name": "PAY-PROD-GW01", "ip_address": "10.0.2.25", "asset_type": "Payment Gateway", "criticality": 95.0, "department": "FinTech Core"},
    {"name": "CUST-DB-PRD01", "ip_address": "10.0.3.50", "asset_type": "Database Server", "criticality": 92.0, "department": "Data Engineering"},
    {"name": "S3-FIN-VAULT-01", "ip_address": "172.16.5.12", "asset_type": "Cloud Storage", "criticality": 88.0, "department": "Finance & Cloud"},
    {"name": "VPN-EDGE-GW02", "ip_address": "198.51.100.1", "asset_type": "VPN Gateway", "criticality": 85.0, "department": "Network Perimeter"},
    {"name": "PORTAL-APP-SRV04", "ip_address": "10.0.4.101", "asset_type": "Application Server", "criticality": 72.0, "department": "Customer Portal"},
    {"name": "ANALYTICS-CLUSTER-02", "ip_address": "10.0.5.200", "asset_type": "Application Server", "criticality": 65.0, "department": "Business Intelligence"},
    {"name": "EXEC-LAPTOP-044", "ip_address": "10.10.12.88", "asset_type": "Workstation", "criticality": 60.0, "department": "Executive Leadership"},
    {"name": "DEV-WORKSTATION-19", "ip_address": "10.10.14.22", "asset_type": "Workstation", "criticality": 40.0, "department": "Engineering"},
    {"name": "WIKI-KNOWLEDGE-BASE", "ip_address": "10.0.6.15", "asset_type": "Internal Wiki", "criticality": 35.0, "department": "HR & Internal Ops"},
]

INCIDENT_SCENARIOS = [
    # Ransomware scenarios
    {
        "title": "BlackCat/ALPHV Ransomware Infiltration & Shadow Copy Deletion",
        "incident_type": "Ransomware",
        "desc_template": "VSSAdmin deletion detected followed by high-speed AES encryption loop on system shares.",
        "sev_range": (85, 99), "sens_range": (75, 95), "users_range": (500, 5000), "sys_range": (15, 80),
        "conf_range": (88, 98), "time_risk": 0.85, "recurrence": 1
    },
    {
        "title": "LockBit 3.0 Ransomware Lateral Movement via PsExec",
        "incident_type": "Ransomware",
        "desc_template": "Active SMB lateral dispersion deploying encryptor binaries across departmental subnets.",
        "sev_range": (82, 98), "sens_range": (70, 92), "users_range": (300, 3500), "sys_range": (10, 60),
        "conf_range": (85, 96), "time_risk": 0.75, "recurrence": 0
    },
    # Data Exfiltration scenarios
    {
        "title": "Mass PII & Credit Card Data Exfiltration via Encrypted Rclone",
        "incident_type": "Data Exfiltration",
        "desc_template": "Outbound Mega.nz TLS data transfer exceeding 250 GB from core transaction warehouse.",
        "sev_range": (80, 96), "sens_range": (88, 99), "users_range": (1000, 8000), "sys_range": (2, 12),
        "conf_range": (86, 96), "time_risk": 0.70, "recurrence": 0
    },
    {
        "title": "Unusual Egress Spike: Database Dump Transfer via DNS Tunneling",
        "incident_type": "Data Exfiltration",
        "desc_template": "Anomalous high-frequency base64 encoded TXT record queries to unverified authoritative nameserver.",
        "sev_range": (75, 90), "sens_range": (80, 95), "users_range": (200, 1500), "sys_range": (1, 5),
        "conf_range": (80, 94), "time_risk": 0.65, "recurrence": 1
    },
    # Privilege Escalation scenarios
    {
        "title": "Active Directory Golden Ticket Forgery & DCSync Extraction",
        "incident_type": "Privilege Escalation",
        "desc_template": "Directory Replication Service (DRSUAPI) invoked by non-domain controller machine account.",
        "sev_range": (78, 95), "sens_range": (75, 90), "users_range": (400, 2500), "sys_range": (3, 10),
        "conf_range": (84, 95), "time_risk": 0.55, "recurrence": 0
    },
    {
        "title": "Linux Kernel Dirty Pipe / PwnKit Privilege Escalation to Root",
        "incident_type": "Privilege Escalation",
        "desc_template": "Local vulnerability exploitation spawned interactive root shell from low-privilege service account.",
        "sev_range": (70, 88), "sens_range": (60, 80), "users_range": (50, 400), "sys_range": (1, 4),
        "conf_range": (82, 92), "time_risk": 0.35, "recurrence": 0
    },
    # Unauthorized Access scenarios
    {
        "title": "Compromised Admin VPN Session with Impossible Travel",
        "incident_type": "Unauthorized Access",
        "desc_template": "Concurrent active sessions detected from London and Tokyo within 8 minutes for privileged user.",
        "sev_range": (65, 85), "sens_range": (60, 80), "users_range": (10, 150), "sys_range": (1, 3),
        "conf_range": (78, 92), "time_risk": 0.80, "recurrence": 1
    },
    {
        "title": "Brute Force Password Spraying against OWA & Azure AD",
        "incident_type": "Unauthorized Access",
        "desc_template": "Distributed source IP addresses spraying common seasonal passwords across 1,200 mailboxes.",
        "sev_range": (55, 75), "sens_range": (50, 70), "users_range": (200, 1200), "sys_range": (2, 6),
        "conf_range": (85, 95), "time_risk": 0.40, "recurrence": 0
    },
    # Insider Threat scenarios
    {
        "title": "Privileged Staff Bulk Source Code & Customer Export to USB",
        "incident_type": "Insider Threat",
        "desc_template": "Massive Git repo bundle archive created and transferred to unapproved external mass storage.",
        "sev_range": (68, 88), "sens_range": (80, 95), "users_range": (50, 500), "sys_range": (1, 2),
        "conf_range": (85, 95), "time_risk": 0.60, "recurrence": 0
    },
    # DDoS scenarios
    {
        "title": "Multi-Vector UDP Amplification & HTTPS Floor Assault",
        "incident_type": "DDoS",
        "desc_template": "Inbound volumetric traffic peaking at 480 Gbps saturating upstream edge peering links.",
        "sev_range": (60, 82), "sens_range": (20, 45), "users_range": (1000, 10000), "sys_range": (5, 20),
        "conf_range": (90, 99), "time_risk": 0.45, "recurrence": 1
    },
    # Malware scenarios
    {
        "title": "Cobalt Strike Beacon Injected into Spoolsv.exe Process",
        "incident_type": "Malware",
        "desc_template": "Memory hollow shellcode execution establishing malleable C2 beacons every 60 seconds.",
        "sev_range": (65, 85), "sens_range": (55, 75), "users_range": (20, 300), "sys_range": (2, 8),
        "conf_range": (82, 94), "time_risk": 0.50, "recurrence": 0
    },
    # Phishing scenarios
    {
        "title": "Executive Spear-Phishing Campaign with Adversary-in-the-Middle Proxy",
        "incident_type": "Phishing",
        "desc_template": "Reverse proxy credential harvest harvesting session cookies bypassing hardware token MFA.",
        "sev_range": (50, 72), "sens_range": (50, 70), "users_range": (10, 80), "sys_range": (1, 3),
        "conf_range": (75, 90), "time_risk": 0.30, "recurrence": 1
    }
]

@router.post("/load")
def load_demo_data(db: Session = Depends(get_db)):
    """
    Clears existing incidents and seeds 10 critical assets and 100 realistic incidents,
    scoring each through the hybrid ML + Rule prioritization pipeline.
    """
    # 1. Ensure Assets exist
    existing_asset_count = db.query(Asset).count()
    if existing_asset_count < len(DEMO_ASSETS):
        db.query(Asset).delete()
        for a_data in DEMO_ASSETS:
            asset = Asset(
                name=a_data["name"],
                ip_address=a_data["ip_address"],
                asset_type=a_data["asset_type"],
                criticality=a_data["criticality"],
                department=a_data["department"]
            )
            db.add(asset)
        db.commit()

    assets = db.query(Asset).all()
    asset_map = {a.name: a for a in assets}

    # 2. Clear old incidents and reports
    db.query(Incident).delete()
    db.commit()

    random.seed(42)
    now = datetime.now(timezone.utc)

    # 3. Generate 100 realistic incidents
    created_incidents = []
    
    for i in range(1, 101):
        scenario = random.choice(INCIDENT_SCENARIOS)
        # Choose asset: high-sev scenarios skew toward critical assets
        if scenario["sev_range"][0] >= 75:
            # Domain Controller, Payment Gateway, Database Server, Cloud Storage
            selected_asset = random.choice(assets[:5])
        else:
            selected_asset = random.choice(assets)

        code = f"INC-{2026000 + i}"
        sev = round(random.uniform(*scenario["sev_range"]), 1)
        sens = round(random.uniform(*scenario["sens_range"]), 1)
        asset_imp = selected_asset.criticality
        conf = round(random.uniform(*scenario["conf_range"]), 1)
        users = random.randint(*scenario["users_range"])
        sys_count = random.randint(*scenario["sys_range"])
        time_r = round(random.uniform(scenario["time_risk"] - 0.1, min(1.0, scenario["time_risk"] + 0.1)), 2)
        rec = scenario["recurrence"] if random.random() < 0.65 else (1 - scenario["recurrence"])
        freq = round(random.uniform(0.1, 0.95), 2)

        norm_users = ml_scorer.normalize_users(users)
        norm_systems = ml_scorer.normalize_systems(sys_count)
        biz_impact = round(0.35 * sev + 0.35 * sens + 0.30 * asset_imp + random.uniform(-4, 4), 1)
        biz_impact = max(0.0, min(100.0, biz_impact))

        type_enc = ml_scorer.encode_incident_type(scenario["incident_type"])
        asset_enc = ml_scorer.encode_asset_type(selected_asset.asset_type)

        factors = {
            "severity": sev,
            "data_sensitivity": sens,
            "asset_importance": asset_imp,
            "attack_confidence": conf,
            "raw_users": users,
            "affected_users_normalized": norm_users,
            "business_impact": biz_impact,
            "incident_type": scenario["incident_type"],
            "asset_type": selected_asset.asset_type,
            "incident_type_encoded": type_enc,
            "asset_type_encoded": asset_enc,
            "time_risk": time_r,
            "historical_frequency": freq,
            "recurrence": rec,
            "raw_systems": sys_count,
            "affected_system_count_normalized": norm_systems
        }

        p_score, ml_sc, rule_sc, p_level, applied_rules = hybrid_prioritizer.calculate_priority(factors)

        factors["priority_score"] = p_score
        contributions = explainability_engine.calculate_factor_contributions(factors)
        mitigations = explainability_engine.get_mitigation_steps(scenario["incident_type"], sev)

        # Status distribution: 60% new, 25% investigating, 10% contained, 5% resolved
        status_roll = random.random()
        if status_roll < 0.60:
            status = "new"
        elif status_roll < 0.85:
            status = "investigating"
        elif status_roll < 0.95:
            status = "contained"
        else:
            status = "resolved"

        # Stagger detection times over the last 5 days
        detected_time = now - timedelta(hours=random.randint(1, 120), minutes=random.randint(0, 59))

        inc = Incident(
            incident_code=code,
            title=f"{scenario['title']} ({selected_asset.name})",
            description=f"{scenario['desc_template']} Target: {selected_asset.name} ({selected_asset.ip_address}).",
            incident_type=scenario["incident_type"],
            status=status,
            asset_id=selected_asset.id,
            asset_name=selected_asset.name,
            asset_type=selected_asset.asset_type,
            severity=sev,
            data_sensitivity=sens,
            asset_importance=asset_imp,
            attack_confidence=conf,
            raw_users=users,
            affected_users_normalized=norm_users,
            business_impact=biz_impact,
            incident_type_encoded=type_enc,
            asset_type_encoded=asset_enc,
            time_risk=time_r,
            historical_frequency=freq,
            recurrence=rec,
            raw_systems=sys_count,
            affected_system_count_normalized=norm_systems,
            ml_score=ml_sc,
            rule_score=rule_sc,
            priority_score=p_score,
            priority_level=p_level,
            factor_contributions_json=json.dumps(contributions),
            mitigation_recommendations_json=json.dumps(mitigations),
            detected_at=detected_time,
            assigned_to=random.choice(["Lead SecOps", "Analyst Alpha", "Analyst Bravo", None])
        )
        created_incidents.append(inc)

    db.bulk_save_objects(created_incidents)
    db.commit()

    # Deterministic Tie-Breaking and Queue Ranking
    all_saved = db.query(Incident).all()
    sorted_all = sorted(all_saved, key=hybrid_prioritizer.tie_break_key)

    for rank, inc in enumerate(sorted_all, 1):
        inc.priority_rank = rank
        if rank == 1:
            inc.why_number_one = explainability_engine.generate_why_number_one(inc)
    db.commit()

    top_inc = sorted_all[0]

    return {
        "message": "Demo environment successfully loaded with 100 prioritized incidents and 10 assets.",
        "total_incidents": len(sorted_all),
        "total_assets": len(assets),
        "top_incident": {
            "code": top_inc.incident_code,
            "title": top_inc.title,
            "priority_score": top_inc.priority_score,
            "priority_level": top_inc.priority_level,
            "why_number_one": top_inc.why_number_one
        }
    }
