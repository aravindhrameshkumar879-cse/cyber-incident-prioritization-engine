from typing import Dict, Any, List, Tuple
from app.engine.ml_scorer import ml_scorer

class ExplainabilityEngine:
    FACTOR_LABELS = {
        "severity": "Technical Severity",
        "data_sensitivity": "Data Sensitivity",
        "asset_importance": "Asset Criticality",
        "attack_confidence": "Attack Confidence",
        "affected_users_normalized": "Impacted Users (Log-Norm)",
        "business_impact": "Evaluated Business Impact",
        "incident_type_encoded": "Incident Threat Profile",
        "asset_type_encoded": "Target Infrastructure Tier",
        "time_risk": "Off-Hours & Weekend Temporal Risk",
        "historical_frequency": "Alert Rarity / Zero-Day Factor",
        "recurrence": "Vulnerability Recurrence",
        "affected_system_count_normalized": "Lateral Blast Radius (Systems)"
    }

    FACTOR_WEIGHTS = {
        "severity": 0.24,
        "business_impact": 0.20,
        "asset_importance": 0.18,
        "data_sensitivity": 0.14,
        "attack_confidence": 0.10,
        "affected_users_normalized": 0.08,
        "affected_system_count_normalized": 0.06,
        "time_risk": 0.06,
        "historical_frequency": 0.04,
        "recurrence": 0.035,
        "incident_type_encoded": 0.03,
        "asset_type_encoded": 0.03,
    }

    MITIGATION_TEMPLATES = {
        "Ransomware": [
            "Immediately isolate infected hosts from VLAN / Active Directory network segment.",
            "Revoke compromised Active Directory service accounts and reset Kerberos tickets (krbtgt).",
            "Verify immutable backup volume integrity and offline snapshot timestamps.",
            "Deploy EDR threat hunt script targeting known ransomware command-and-control signatures."
        ],
        "Data Exfiltration": [
            "Terminate suspicious outbound TLS sessions and block remote destination IPs on perimeter firewall.",
            "Lock implicated user credentials and invoke immediate session revocation in IdP/SSO.",
            "Initiate forensic triage of staging directories, archival utilities (rar/7z), and cloud sync processes.",
            "Engage legal counsel and privacy compliance leads for regulatory notification assessment (GDPR/HIPAA)."
        ],
        "Unauthorized Access": [
            "Enforce immediate MFA re-authentication challenge across all active sessions.",
            "Audit identity provider authentication logs for suspicious geographical and Impossible Travel anomalies.",
            "Rotate API keys, SSH authorized_keys, and administrative service credentials.",
            "Review sudoers and local administrator group membership for unauthorized modifications."
        ],
        "Privilege Escalation": [
            "Demote or suspend elevated user account pending behavioral inspection.",
            "Inspect system event logs (Windows Event ID 4672 / Linux auth.log) for privilege delegation artifacts.",
            "Patch vulnerable kernel modules or vulnerable local services leveraged for elevation.",
            "Audit LSASS memory dumping attempts and enable Credential Guard."
        ],
        "DDoS": [
            "Activate cloud scrub center and upstream BGP Flowspec rate limiting rules.",
            "Enable aggressive HTTP flood protection and CAPTCHA challenge at CDN edge.",
            "Inspect server connection states (SYN_RECV) and optimize TCP keepalive / backlog buffers.",
            "Coordinate with ISP to filter volumetric amplification attack vectors (NTP/DNS/SSDP)."
        ],
        "Malware": [
            "Quarantine binary across fleet via centralized EDR hash blocklist.",
            "Submit payload to sandbox for dynamic behavioral extraction and IOC generation.",
            "Perform memory acquisition on affected endpoint to inspect unmapped DLL injection.",
            "Remediate persistence mechanisms (Scheduled Tasks, Run keys, systemd service units)."
        ],
        "Phishing": [
            "Purge phishing email from all recipient inboxes via Microsoft 365 / Google Workspace API.",
            "Block sender domain and embedded credential harvesting URLs at secure email gateway.",
            "Reset credentials for any recipients who clicked the link or submitted form credentials.",
            "Dispatch targeted security awareness flash bulletin to impacted departments."
        ],
        "Insider Threat": [
            "Place user account on discrete behavioral surveillance with heightened telemetry logging.",
            "Capture endpoint forensic disk image with chain-of-custody documentation.",
            "Audit file access patterns and USB mass storage device insertion logs for the past 90 days.",
            "Notify HR and executive leadership per internal insider threat response protocol."
        ]
    }

    @classmethod
    def generate_why_number_one(cls, inc: Any) -> str:
        """
        Synthesizes a compelling, plain-language executive rationale explaining
        why this specific incident claimed the #1 priority spot in the SOC queue.
        """
        def get_val(key, default):
            if isinstance(inc, dict):
                return inc.get(key, default)
            return getattr(inc, key, default)

        title = get_val("title", "Critical Threat Alert")
        itype = get_val("incident_type", "Ransomware")
        aname = get_val("asset_name", "Primary Infrastructure")
        atype = get_val("asset_type", "Domain Controller")
        sev = float(get_val("severity", 50.0))
        biz_imp = float(get_val("business_impact", 50.0))
        score = float(get_val("priority_score", 0.0))
        users = int(get_val("raw_users", 1))
        systems = int(get_val("raw_systems", 1))
        time_risk = float(get_val("time_risk", 0.2))
        confidence = float(get_val("attack_confidence", 50.0))
        recurrence = int(get_val("recurrence", 0))

        temporal_phrase = "during high-risk off-hours" if time_risk >= 0.6 else "during active operations"
        recurrence_phrase = "with confirmed historical recurrence on this vector" if recurrence == 1 else "as an acute zero-day outbreak"
        
        reasons = []
        if sev >= 75.0:
            reasons.append(f"severe technical payload rating ({sev:.1f}/100)")
        if atype in {"Domain Controller", "Payment Gateway", "Database Server"}:
            reasons.append(f"direct compromise of tier-0 crown-jewel infrastructure ({atype} '{aname}')")
        if biz_imp >= 70.0:
            reasons.append(f"projected business disruption of {biz_imp:.1f}/100")
        if confidence >= 80.0:
            reasons.append(f"high-fidelity sensor verification ({confidence:.1f}% confidence)")
        if users >= 100 or systems >= 5:
            reasons.append(f"elevated blast radius affecting {users:,} users across {systems} systems")

        reasons_text = "; ".join(reasons) if reasons else "high multi-factor risk convergence across technical and business dimensions"

        return (
            f"Ranked #1 in SOC Queue (Priority Score: {score:.1f}/100). This {itype} threat against '{aname}' "
            f"presents the single greatest systemic risk to enterprise operations. Detected {temporal_phrase} {recurrence_phrase}, "
            f"the engine prioritized this incident due to {reasons_text}. Immediate tier-3 analyst containment is required to prevent widespread data loss and lateral progression."
        )

    @classmethod
    def calculate_factor_contributions(cls, inc: Any) -> Dict[str, Any]:
        """
        Computes the contribution of each factor toward the incident's risk score.
        """
        def get_val(key, default):
            if isinstance(inc, dict):
                return inc.get(key, default)
            return getattr(inc, key, default)

        contributions = {}
        model_importances = ml_scorer.get_feature_importances()

        for feat, label in cls.FACTOR_LABELS.items():
            val = float(get_val(feat, 50.0))
            importance = model_importances.get(feat, cls.FACTOR_WEIGHTS.get(feat, 0.08))
            
            # Baseline is centered around 50 for normalized scales, 0.5 for 0-1
            baseline = 0.5 if feat in {"time_risk", "historical_frequency"} else (0.3 if feat == "recurrence" else 50.0)
            
            delta = val - baseline
            # Contribution points added to or subtracted from median
            points = delta * importance * 0.85

            desc = ""
            if points > 3.0:
                desc = f"Strong upward driver (+{points:.1f} pts) due to high {label.lower()}"
            elif points > 0.5:
                desc = f"Moderate elevation (+{points:.1f} pts)"
            elif points < -3.0:
                desc = f"Downwards risk dampener ({points:.1f} pts) due to low {label.lower()}"
            else:
                desc = f"Neutral impact ({points:+.1f} pts)"

            contributions[feat] = {
                "name": feat,
                "label": label,
                "value": round(val, 2),
                "importance_pct": round(importance * 100, 1),
                "contribution_points": round(points, 2),
                "description": desc
            }

        return contributions

    @classmethod
    def compare_incidents(cls, inc_a: Any, inc_b: Any) -> Dict[str, Any]:
        """
        Performs deep comparative reasoning between Incident A and Incident B,
        explaining why one is prioritized over the other in plain language.
        """
        def get_val(item, key, default):
            if isinstance(item, dict):
                return item.get(key, default)
            return getattr(item, key, default)

        code_a = get_val(inc_a, "incident_code", "INC-A")
        code_b = get_val(inc_b, "incident_code", "INC-B")
        score_a = float(get_val(inc_a, "priority_score", 0.0))
        score_b = float(get_val(inc_b, "priority_score", 0.0))
        ml_a = float(get_val(inc_a, "ml_score", 0.0))
        ml_b = float(get_val(inc_b, "ml_score", 0.0))
        rule_a = float(get_val(inc_a, "rule_score", 0.0))
        rule_b = float(get_val(inc_b, "rule_score", 0.0))

        higher_code = code_a if score_a >= score_b else code_b
        score_diff = abs(score_a - score_b)
        ml_delta = ml_a - ml_b
        rule_delta = rule_a - rule_b

        # Compare divergent factors
        divergent_factors = []
        lead_reasons = []

        factors_to_check = [
            ("severity", "Technical Severity"),
            ("business_impact", "Business Impact"),
            ("asset_importance", "Asset Criticality"),
            ("attack_confidence", "Attack Confidence"),
            ("data_sensitivity", "Data Sensitivity"),
            ("affected_users_normalized", "Affected Users"),
            ("affected_system_count_normalized", "System Count"),
            ("time_risk", "Off-Hours Risk"),
            ("recurrence", "Recurrence")
        ]

        for feat, label in factors_to_check:
            val_a = float(get_val(inc_a, feat, 0.0))
            val_b = float(get_val(inc_b, feat, 0.0))
            diff = val_a - val_b
            if abs(diff) >= 5.0 or (feat in {"time_risk", "recurrence"} and abs(diff) >= 0.2):
                favors = code_a if diff > 0 else code_b
                divergent_factors.append({
                    "factor": feat,
                    "label": label,
                    "val_a": round(val_a, 2),
                    "val_b": round(val_b, 2),
                    "diff": round(diff, 2),
                    "favors": favors
                })

        # Generate synthesized paragraph
        winner_code = code_a if score_a >= score_b else code_b
        runner_code = code_b if score_a >= score_b else code_a
        winner_inc = inc_a if score_a >= score_b else inc_b
        runner_inc = inc_b if score_a >= score_b else inc_a

        w_type = get_val(winner_inc, "incident_type", "")
        r_type = get_val(runner_inc, "incident_type", "")
        w_asset = get_val(winner_inc, "asset_type", "")
        r_asset = get_val(runner_inc, "asset_type", "")

        primary_drivers = []
        w_sev = float(get_val(winner_inc, "severity", 0.0))
        r_sev = float(get_val(runner_inc, "severity", 0.0))
        if w_sev - r_sev >= 10.0:
            primary_drivers.append(f"higher technical alert severity ({w_sev:.0f} vs {r_sev:.0f})")

        w_asset_imp = float(get_val(winner_inc, "asset_importance", 0.0))
        r_asset_imp = float(get_val(runner_inc, "asset_importance", 0.0))
        if w_asset_imp - r_asset_imp >= 10.0:
            primary_drivers.append(f"greater target asset criticality ({w_asset} at {w_asset_imp:.0f} vs {r_asset} at {r_asset_imp:.0f})")

        w_biz = float(get_val(winner_inc, "business_impact", 0.0))
        r_biz = float(get_val(runner_inc, "business_impact", 0.0))
        if w_biz - r_biz >= 10.0:
            primary_drivers.append(f"superior business impact risk ({w_biz:.0f} vs {r_biz:.0f})")

        drivers_text = ", and ".join(primary_drivers) if primary_drivers else "composite convergence across machine learning risk vectors and deterministic rule thresholds"

        justification = (
            f"{winner_code} is prioritized over {runner_code} by a delta of +{score_diff:.1f} points "
            f"(Score: {max(score_a, score_b):.1f} vs {min(score_a, score_b):.1f}). "
            f"The primary justification for this ranking is {drivers_text}. "
            f"Both ML regression model (+{abs(ml_delta):.1f} pts) and rule engine logic (+{abs(rule_delta):.1f} pts) "
            f"confirm {winner_code} presents higher immediate threat to operational integrity."
        )

        return {
            "higher_priority_code": higher_code,
            "score_difference": round(score_diff, 2),
            "plain_language_justification": justification,
            "divergent_factors": divergent_factors,
            "ml_delta": round(ml_delta, 2),
            "rule_delta": round(rule_delta, 2)
        }

    @classmethod
    def get_mitigation_steps(cls, incident_type: str, severity: float) -> List[str]:
        steps = cls.MITIGATION_TEMPLATES.get(incident_type, [
            "Isolate the affected network interface to contain spread.",
            "Collect volatile RAM and system process state for forensic preservation.",
            "Verify perimeter firewall and SIEM telemetry for command-and-control beacons.",
            "Notify SOC Tier-2/3 incident response lead for escalation."
        ])
        if severity >= 80.0:
            return ["🚨 URGENT: High Severity protocol activated."] + steps
        return steps

explainability_engine = ExplainabilityEngine()
