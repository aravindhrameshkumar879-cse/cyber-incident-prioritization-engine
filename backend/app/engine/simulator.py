from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.engine.hybrid_prioritizer import hybrid_prioritizer, classify_priority_level
from app.engine.explainability import explainability_engine
from app.models.incident import Incident

class SimulatorEngine:
    @staticmethod
    def simulate_scenario(factors: Dict[str, Any], db: Optional[Session] = None) -> Dict[str, Any]:
        """
        Executes a real-time, non-persistent what-if simulation on risk parameters.
        """
        # Calculate hybrid scores
        p_score, ml_score, rule_score, p_level, applied_rules = hybrid_prioritizer.calculate_priority(factors)

        # Baseline comparison if incident_id was provided
        baseline_score = None
        baseline_level = None
        score_delta = 0.0
        orig_rank = None
        est_new_rank = 1
        rank_shift = 0

        incident_id = factors.get("incident_id")
        if incident_id and db:
            orig_inc = db.query(Incident).filter(Incident.id == incident_id).first()
            if orig_inc:
                baseline_score = orig_inc.priority_score
                baseline_level = orig_inc.priority_level
                orig_rank = orig_inc.priority_rank
                score_delta = round(p_score - baseline_score, 2)

        # Calculate estimated new rank against active queue in DB if available
        if db:
            active_incidents = db.query(Incident).filter(Incident.status.in_(["new", "investigating"])).all()
            if active_incidents:
                # Count how many existing incidents have a higher priority key
                sim_factors = dict(factors)
                sim_factors["priority_score"] = p_score
                sim_key = hybrid_prioritizer.tie_break_key(sim_factors)
                
                higher_count = sum(
                    1 for inc in active_incidents
                    if inc.id != incident_id and hybrid_prioritizer.tie_break_key(inc) < sim_key
                )
                est_new_rank = higher_count + 1
                if orig_rank:
                    rank_shift = orig_rank - est_new_rank  # Positive means moved up in priority

        # Explanations
        factors_with_score = dict(factors)
        factors_with_score["priority_score"] = p_score
        contributions = explainability_engine.calculate_factor_contributions(factors_with_score)
        
        direction_phrase = f"{'+' if score_delta >= 0 else ''}{score_delta:.1f} pts"
        rank_phrase = f"shifting estimated queue position to #{est_new_rank} ({'+' if rank_shift > 0 else ''}{rank_shift} spots)" if orig_rank else f"projected queue position: #{est_new_rank}"
        
        summary = (
            f"Simulated Priority: {p_score:.1f}/100 ({p_level}). "
            f"Resulting from 65% ML Score ({ml_score:.1f}) + 35% Rule Score ({rule_score:.1f}). "
            f"{f'Delta from original: {direction_phrase}, {rank_phrase}. ' if baseline_score is not None else ''}"
            f"Key risk driver: {max(contributions.values(), key=lambda x: x['contribution_points'])['label']}."
        )

        mitigations = explainability_engine.get_mitigation_steps(
            factors.get("incident_type", "Ransomware"),
            float(factors.get("severity", 50.0))
        )

        return {
            "simulated_priority_score": p_score,
            "simulated_priority_level": p_level,
            "ml_score": ml_score,
            "rule_score": rule_score,
            "estimated_rank_shift": rank_shift,
            "estimated_new_rank": est_new_rank,
            "baseline_score": baseline_score,
            "baseline_level": baseline_level,
            "score_delta": score_delta,
            "factor_contributions": contributions,
            "explainability_summary": summary,
            "mitigation_recommendations": mitigations
        }

simulator_engine = SimulatorEngine()
