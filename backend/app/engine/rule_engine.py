from typing import Dict, Any, List, Tuple

class RuleEngine:
    """
    Deterministic context-aware rule engine (35% weight).
    Applies business logic, asset criticality boosts, off-hours risk multipliers,
    and historical recurrence penalties.
    """

    CRITICAL_ASSETS = {"Domain Controller", "Payment Gateway", "Database Server"}
    HIGH_IMPACT_INCIDENTS = {"Ransomware", "Data Exfiltration"}
    MEDIUM_IMPACT_INCIDENTS = {"Privilege Escalation", "Unauthorized Access", "Insider Threat"}

    def evaluate(self, factors: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calculates deterministic rule score and returns (score, applied_rules).
        """
        severity = float(factors.get("severity", 50.0))
        data_sens = float(factors.get("data_sensitivity", 50.0))
        biz_impact = float(factors.get("business_impact", 50.0))
        asset_imp = float(factors.get("asset_importance", 50.0))
        asset_type = str(factors.get("asset_type", ""))
        incident_type = str(factors.get("incident_type", ""))
        time_risk = float(factors.get("time_risk", 0.2))
        recurrence = int(factors.get("recurrence", 0))
        raw_systems = int(factors.get("raw_systems", 1))
        attack_conf = float(factors.get("attack_confidence", 50.0))

        applied_rules = []

        # 1. Base Score (Technical & Business foundation)
        base = 0.35 * severity + 0.35 * data_sens + 0.30 * biz_impact
        current_score = base
        applied_rules.append({
            "rule": "Base Context Assessment",
            "impact": round(base, 2),
            "description": f"Weighted baseline from severity ({severity:.1f}), data sensitivity ({data_sens:.1f}), and business impact ({biz_impact:.1f})"
        })

        # 2. Asset Criticality Boost
        if asset_imp >= 85.0:
            boost = 15.0
            current_score += boost
            applied_rules.append({
                "rule": "Tier-0 Critical Asset Rule",
                "impact": boost,
                "description": f"Asset importance ({asset_imp:.1f}) exceeds tier-0 threshold (>=85)"
            })
        elif asset_imp >= 65.0:
            boost = 8.0
            current_score += boost
            applied_rules.append({
                "rule": "High Criticality Asset Rule",
                "impact": boost,
                "description": f"Asset importance ({asset_imp:.1f}) is elevated (>=65)"
            })

        # 3. High-Value Infrastructure Target
        if asset_type in self.CRITICAL_ASSETS:
            boost = 10.0
            current_score += boost
            applied_rules.append({
                "rule": "Crown-Jewel Infrastructure Target",
                "impact": boost,
                "description": f"Target asset '{asset_type}' is classified as mission-critical enterprise infrastructure"
            })

        # 4. Severe Threat Category Elevation
        if incident_type in self.HIGH_IMPACT_INCIDENTS:
            boost = 12.0
            current_score += boost
            applied_rules.append({
                "rule": "Critical Threat Vector Rule",
                "impact": boost,
                "description": f"Incident signature '{incident_type}' carries existential enterprise risk"
            })
        elif incident_type in self.MEDIUM_IMPACT_INCIDENTS:
            boost = 6.0
            current_score += boost
            applied_rules.append({
                "rule": "Elevated Threat Vector Rule",
                "impact": boost,
                "description": f"Incident signature '{incident_type}' represents an active internal compromise"
            })

        # 5. Temporal / Off-Hours Risk Multiplier
        if time_risk >= 0.6:
            multiplier_boost = current_score * 0.12
            current_score += multiplier_boost
            applied_rules.append({
                "rule": "Off-Hours & Weekend Multiplier",
                "impact": round(multiplier_boost, 2),
                "description": f"Detected during high-risk temporal window (time risk {time_risk:.2f} >= 0.60) when SOC response capacity is constrained"
            })

        # 6. Historical Recurrence Penalty
        if recurrence == 1:
            boost = 8.0
            current_score += boost
            applied_rules.append({
                "rule": "Persistent Campaign / Recurrence Flag",
                "impact": boost,
                "description": "Historical recurrence detected: repeated attack vector indicating an unresolved vulnerability or persistent threat campaign"
            })

        # 7. Blast Radius / Multi-system Impact
        if raw_systems >= 50:
            boost = 10.0
            current_score += boost
            applied_rules.append({
                "rule": "Massive Blast Radius Rule",
                "impact": boost,
                "description": f"Widespread systemic blast radius affecting {raw_systems} systems (>=50)"
            })
        elif raw_systems >= 10:
            boost = 5.0
            current_score += boost
            applied_rules.append({
                "rule": "Multi-System Infection Rule",
                "impact": boost,
                "description": f"Multi-host lateral movement confirmed across {raw_systems} systems (>=10)"
            })

        # 8. High Attack Certainty
        if attack_conf >= 85.0:
            boost = 5.0
            current_score += boost
            applied_rules.append({
                "rule": "High-Fidelity Evidence Rule",
                "impact": boost,
                "description": f"Attack confidence is verified at {attack_conf:.1f}%, ruling out false positive heuristics"
            })

        final_score = float(max(0.0, min(100.0, current_score)))
        return round(final_score, 2), applied_rules

rule_engine = RuleEngine()
