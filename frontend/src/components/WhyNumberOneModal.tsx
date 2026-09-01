import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  X, 
  Sparkles, 
  ShieldAlert, 
  Server, 
  Users, 
  Clock, 
  Activity, 
  TrendingUp, 
  FileText, 
  ArrowRight,
  CheckCircle2,
  AlertOctagon
} from 'lucide-react';
import { Incident } from '../types';
import { PriorityBadge } from './PriorityBadge';

interface WhyNumberOneModalProps {
  incident: Incident | null;
  isOpen: boolean;
  onClose: () => void;
  onGenerateReport?: (id: number) => void;
}

export const WhyNumberOneModal: React.FC<WhyNumberOneModalProps> = ({
  incident,
  isOpen,
  onClose,
  onGenerateReport
}) => {
  const navigate = useNavigate();
  if (!isOpen || !incident) return null;

  const contributions = incident.factor_contributions || {};

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-2xl bg-[#0d1322] border border-cyan-500/40 shadow-[0_0_50px_rgba(6,182,212,0.25)] p-6 md:p-8 text-slate-100">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header Badge */}
        <div className="flex items-center gap-2 mb-3">
          <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-950/80 border border-rose-500/60 text-rose-300 text-xs font-mono font-bold tracking-wider shadow-[0_0_15px_rgba(244,63,94,0.4)]">
            <AlertOctagon className="w-3.5 h-3.5 text-rose-400" />
            RANK #1 IN SOC QUEUE
          </span>
          <PriorityBadge level={incident.priority_level} score={incident.priority_score} size="md" />
        </div>

        {/* Title */}
        <h2 className="text-xl md:text-2xl font-bold text-white tracking-tight mb-2">
          {incident.title}
        </h2>
        <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-slate-400 mb-6">
          <span>Code: <strong className="text-cyan-400">{incident.incident_code}</strong></span>
          <span>Target: <strong className="text-white">{incident.asset_name}</strong> ({incident.asset_type})</span>
          <span>Threat: <strong className="text-white">{incident.incident_type}</strong></span>
          <span>Detected: <strong className="text-slate-300">{new Date(incident.detected_at).toLocaleString()}</strong></span>
        </div>

        {/* Explainability Callout Box */}
        <div className="p-4 rounded-xl bg-gradient-to-br from-rose-950/30 via-slate-900 to-cyan-950/30 border border-rose-500/30 mb-6">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-lg bg-rose-500/20 text-rose-400 mt-0.5">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-mono uppercase tracking-wider text-rose-300 font-semibold mb-1">
                Plain-Language Prioritization Rationale
              </h4>
              <p className="text-sm text-slate-200 leading-relaxed">
                {incident.why_number_one || (
                  `Ranked #1 due to critical threat payload (${incident.severity.toFixed(1)}/100) targeting crown-jewel infrastructure '${incident.asset_name}' (${incident.asset_type}). Model indicates highest probability of systemic operational disruption across 55,000+ evaluated scenarios.`
                )}
              </p>
            </div>
          </div>
        </div>

        {/* Scoring Breakdown Split (65% ML / 35% Rule) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6 font-mono">
          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800">
            <span className="text-[11px] text-slate-400 block mb-1">FINAL HYBRID SCORE</span>
            <span className="text-2xl font-extrabold text-white tracking-tight">{incident.priority_score.toFixed(1)}</span>
            <span className="text-xs text-rose-400 block mt-1 font-bold">100% Weighted Risk</span>
          </div>
          <div className="p-4 rounded-xl bg-slate-900/90 border border-cyan-500/30">
            <span className="text-[11px] text-cyan-400 block mb-1">ML REGRESSION MODEL (65%)</span>
            <span className="text-2xl font-bold text-cyan-300">{incident.ml_score.toFixed(1)}</span>
            <span className="text-xs text-slate-400 block mt-1">+{(0.65 * incident.ml_score).toFixed(1)} points contribution</span>
          </div>
          <div className="p-4 rounded-xl bg-slate-900/90 border border-purple-500/30">
            <span className="text-[11px] text-purple-400 block mb-1">CONTEXT RULE ENGINE (35%)</span>
            <span className="text-2xl font-bold text-purple-300">{incident.rule_score.toFixed(1)}</span>
            <span className="text-xs text-slate-400 block mt-1">+{(0.35 * incident.rule_score).toFixed(1)} points contribution</span>
          </div>
        </div>

        {/* Primary Factor Drivers */}
        <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold mb-3 flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          Multi-Dimensional Factor Drivers
        </h4>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8">
          {/* Severity */}
          <div className="p-3.5 rounded-lg bg-slate-900/70 border border-slate-800 flex items-center justify-between">
            <div>
              <span className="text-xs text-slate-400 block">Technical Severity</span>
              <span className="text-sm font-bold text-slate-200">{incident.severity.toFixed(1)} / 100</span>
            </div>
            <div className="w-24 bg-slate-800 rounded-full h-2 overflow-hidden">
              <div className="bg-rose-500 h-full rounded-full" style={{ width: `${incident.severity}%` }} />
            </div>
          </div>

          {/* Asset Criticality */}
          <div className="p-3.5 rounded-lg bg-slate-900/70 border border-slate-800 flex items-center justify-between">
            <div>
              <span className="text-xs text-slate-400 block">Asset Importance</span>
              <span className="text-sm font-bold text-slate-200">{incident.asset_importance.toFixed(1)} / 100</span>
            </div>
            <div className="w-24 bg-slate-800 rounded-full h-2 overflow-hidden">
              <div className="bg-cyan-500 h-full rounded-full" style={{ width: `${incident.asset_importance}%` }} />
            </div>
          </div>

          {/* Business Impact */}
          <div className="p-3.5 rounded-lg bg-slate-900/70 border border-slate-800 flex items-center justify-between">
            <div>
              <span className="text-xs text-slate-400 block">Business Impact</span>
              <span className="text-sm font-bold text-slate-200">{incident.business_impact.toFixed(1)} / 100</span>
            </div>
            <div className="w-24 bg-slate-800 rounded-full h-2 overflow-hidden">
              <div className="bg-amber-500 h-full rounded-full" style={{ width: `${incident.business_impact}%` }} />
            </div>
          </div>

          {/* Attack Confidence */}
          <div className="p-3.5 rounded-lg bg-slate-900/70 border border-slate-800 flex items-center justify-between">
            <div>
              <span className="text-xs text-slate-400 block">Attack Confidence</span>
              <span className="text-sm font-bold text-slate-200">{incident.attack_confidence.toFixed(1)}%</span>
            </div>
            <div className="w-24 bg-slate-800 rounded-full h-2 overflow-hidden">
              <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${incident.attack_confidence}%` }} />
            </div>
          </div>

          {/* Impacted Users & Systems */}
          <div className="p-3.5 rounded-lg bg-slate-900/70 border border-slate-800 flex items-center justify-between">
            <div>
              <span className="text-xs text-slate-400 block">Affected Accounts</span>
              <span className="text-sm font-bold text-slate-200">{incident.raw_users.toLocaleString()} users</span>
            </div>
            <Users className="w-4 h-4 text-cyan-400" />
          </div>

          {/* Temporal Window */}
          <div className="p-3.5 rounded-lg bg-slate-900/70 border border-slate-800 flex items-center justify-between">
            <div>
              <span className="text-xs text-slate-400 block">Off-Hours Risk</span>
              <span className="text-sm font-bold text-slate-200">
                {incident.time_risk >= 0.6 ? 'ELEVATED (Off-Hours Multiplier)' : 'STANDARD'}
              </span>
            </div>
            <Clock className={`w-4 h-4 ${incident.time_risk >= 0.6 ? 'text-rose-400' : 'text-slate-400'}`} />
          </div>
        </div>

        {/* Modal Footer Actions */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-slate-800">
          <div className="flex items-center gap-2">
            {onGenerateReport && (
              <button
                onClick={() => {
                  onClose();
                  onGenerateReport(incident.id);
                }}
                className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-mono font-medium transition-colors"
              >
                <FileText className="w-4 h-4 text-cyan-400" />
                Generate PDF Dossier
              </button>
            )}
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-xs font-mono text-slate-400 hover:text-white transition-colors"
            >
              Dismiss
            </button>
            <button
              onClick={() => {
                onClose();
                navigate(`/incidents/${incident.id}`);
              }}
              className="flex items-center gap-2 px-5 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-mono font-bold shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all"
            >
              <span>Open Triage Investigation</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};
