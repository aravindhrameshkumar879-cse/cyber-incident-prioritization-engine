import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  FileText, 
  Scale, 
  SlidersHorizontal, 
  CheckCircle2, 
  Clock, 
  ShieldAlert, 
  Activity, 
  Server, 
  Users, 
  AlertTriangle, 
  Sparkles,
  ChevronDown
} from 'lucide-react';
import { Incident, IncidentStatus } from '../types';
import { api } from '../services/api';
import { PriorityBadge } from '../components/PriorityBadge';
import { StatusBadge } from '../components/StatusBadge';
import { ScoreGauge } from '../components/ScoreGauge';
import { ComparativeModal } from '../components/ComparativeModal';

export const IncidentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [incident, setIncident] = useState<Incident | null>(null);
  const [allIncidents, setAllIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const [compareOpen, setCompareOpen] = useState(false);
  const [notification, setNotification] = useState<string | null>(null);

  const fetchIncidentData = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const data = await api.getIncident(Number(id));
      setIncident(data);

      // Also get queue for comparative selector
      const queue = await api.getRankedIncidents(undefined, undefined, 50, 0);
      setAllIncidents(queue.items);
    } catch (err: any) {
      alert(`Error loading incident: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidentData();
  }, [id]);

  const handleStatusChange = async (newStatus: IncidentStatus) => {
    if (!incident) return;
    try {
      setUpdatingStatus(true);
      const updated = await api.updateIncidentStatus(incident.id, newStatus);
      setIncident(updated);
      setNotification(`Status updated to ${newStatus.toUpperCase()}`);
      setTimeout(() => setNotification(null), 3000);
    } catch (err: any) {
      alert(`Error updating status: ${err.message}`);
    } finally {
      setUpdatingStatus(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!incident) return;
    try {
      setNotification('Generating ReportLab PDF dossier...');
      const rep = await api.generateReport(incident.id, 'executive');
      setNotification('PDF generated! Opening download...');
      window.open(rep.download_url, '_blank');
      setTimeout(() => setNotification(null), 4000);
    } catch (err: any) {
      alert(`Error generating PDF: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center font-mono text-slate-400">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p>Loading incident telemetry and explainability model...</p>
        </div>
      </div>
    );
  }

  if (!incident) {
    return (
      <div className="min-h-screen flex items-center justify-center font-mono text-slate-400">
        <div className="text-center space-y-4">
          <p>Incident not found.</p>
          <Link to="/" className="px-4 py-2 rounded-lg bg-slate-800 text-cyan-400 border border-slate-700">
            Back to Queue
          </Link>
        </div>
      </div>
    );
  }

  const contributions = incident.factor_contributions || {};

  return (
    <div className="min-h-screen max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Toast Notification */}
      {notification && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 border border-cyan-500/50 text-cyan-300 text-xs font-mono shadow-[0_0_20px_rgba(6,182,212,0.3)] animate-slide-up">
          <CheckCircle2 className="w-4 h-4 text-cyan-400" />
          <span>{notification}</span>
        </div>
      )}

      {/* Top Breadcrumb & Action Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-xs font-mono text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Triage Queue</span>
        </button>

        <div className="flex flex-wrap items-center gap-2">
          {/* Compare Button */}
          <button
            onClick={() => setCompareOpen(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-850 hover:bg-slate-800 text-slate-200 border border-slate-700 text-xs font-mono transition-colors"
          >
            <Scale className="w-4 h-4 text-purple-400" />
            <span>Compare Priority</span>
          </button>

          {/* Simulator Link */}
          <button
            onClick={() => navigate(`/simulator?incident_id=${incident.id}`)}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-850 hover:bg-slate-800 text-slate-200 border border-slate-700 text-xs font-mono transition-colors"
          >
            <SlidersHorizontal className="w-4 h-4 text-cyan-400" />
            <span>Simulate What-If</span>
          </button>

          {/* PDF Report Generation */}
          <button
            onClick={handleGenerateReport}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-mono font-bold shadow-[0_0_15px_rgba(6,182,212,0.25)] transition-all"
          >
            <FileText className="w-4 h-4" />
            <span>Generate PDF Dossier</span>
          </button>
        </div>
      </div>

      {/* Main Incident Dossier Header */}
      <div className="p-6 md:p-8 rounded-2xl bg-gradient-to-r from-slate-900 via-[#0d1322] to-slate-900 border border-slate-800 shadow-2xl">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div className="space-y-3 max-w-3xl">
            <div className="flex flex-wrap items-center gap-3">
              <span className="font-mono text-sm font-bold text-cyan-400">
                {incident.incident_code}
              </span>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                Rank #{incident.priority_rank} in SOC Queue
              </span>
              <PriorityBadge level={incident.priority_level} score={incident.priority_score} size="md" />
              
              {/* Status Selector Dropdown */}
              <div className="relative inline-block">
                <select
                  value={incident.status}
                  disabled={updatingStatus}
                  onChange={(e) => handleStatusChange(e.target.value as IncidentStatus)}
                  className="bg-slate-850 border border-slate-700 text-slate-200 text-xs font-mono rounded-lg px-2.5 py-1 focus:outline-none focus:border-cyan-400 cursor-pointer uppercase"
                >
                  <option value="new">Status: NEW ALERT</option>
                  <option value="investigating">Status: INVESTIGATING</option>
                  <option value="contained">Status: CONTAINED</option>
                  <option value="resolved">Status: RESOLVED</option>
                </select>
              </div>
            </div>

            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              {incident.title}
            </h1>

            <p className="text-xs md:text-sm text-slate-300 font-mono">
              Target: <strong className="text-cyan-400">{incident.asset_name}</strong> ({incident.asset_type}) &bull; Threat: <strong className="text-white">{incident.incident_type}</strong> &bull; Detected: <strong className="text-slate-400">{new Date(incident.detected_at).toUTCString()}</strong>
            </p>

            <p className="text-xs text-slate-400 leading-relaxed max-w-2xl">
              {incident.description}
            </p>
          </div>

          {/* Right Gauge */}
          <div className="border-t lg:border-t-0 lg:border-l border-slate-800 pt-4 lg:pt-0 lg:pl-8 shrink-0">
            <ScoreGauge
              score={incident.priority_score}
              mlScore={incident.ml_score}
              ruleScore={incident.rule_score}
              level={incident.priority_level}
              size="lg"
            />
          </div>
        </div>
      </div>

      {/* Explainability Callout */}
      <div className="p-6 rounded-2xl bg-gradient-to-br from-cyan-950/20 via-slate-900 to-purple-950/20 border border-cyan-500/30">
        <div className="flex items-start gap-3">
          <div className="p-2.5 rounded-xl bg-cyan-500/20 text-cyan-400 mt-0.5">
            <Sparkles className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <h3 className="text-xs font-mono uppercase tracking-wider text-cyan-300 font-bold">
              Automated Explainable AI & Context Reasoning
            </h3>
            <p className="text-sm text-slate-200 leading-relaxed">
              {incident.why_number_one || (
                `Incident prioritized at ${incident.priority_score.toFixed(1)}/100 based on composite signals. The 65% machine learning regression model estimated high systemic impact from severity (${incident.severity.toFixed(1)}) and asset criticality (${incident.asset_importance.toFixed(1)}). The 35% deterministic rule engine applied infrastructure and threat multipliers.`
              )}
            </p>
          </div>
        </div>
      </div>

      {/* 12 Contextual Feature Breakdown Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-mono uppercase tracking-wider text-slate-300 font-bold flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            12-Feature Pipeline Contributions
          </h3>
          <span className="text-xs font-mono text-slate-500">
            Trained on 55,000+ scenarios with StandardScaler normalization
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(contributions).map(([key, item]) => {
            const isPositive = item.contribution_points > 0;
            return (
              <div key={key} className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-slate-300 font-semibold">{item.label}</span>
                    <span className={`text-xs font-mono font-bold ${isPositive ? 'text-rose-400' : 'text-slate-400'}`}>
                      {isPositive ? `+${item.contribution_points.toFixed(1)} pts` : `${item.contribution_points.toFixed(1)} pts`}
                    </span>
                  </div>
                  <div className="flex items-baseline gap-2 mb-2">
                    <span className="text-xl font-bold font-mono text-white">
                      {item.value.toFixed(1)}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">
                      (Model Weight: {item.importance_pct.toFixed(1)}%)
                    </span>
                  </div>
                </div>
                <p className="text-[11px] text-slate-400 font-mono leading-normal pt-2 border-t border-slate-800/80">
                  {item.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Actionable Containment & Mitigation Checklist */}
      <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-mono uppercase tracking-wider text-white font-bold flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-cyan-400" />
            Prescribed Incident Containment Checklist
          </h3>
          <span className="text-xs font-mono text-cyan-400">
            Remediation Playbook: {incident.incident_type}
          </span>
        </div>

        <div className="space-y-2.5">
          {(incident.mitigation_recommendations || []).map((step, idx) => (
            <div key={idx} className="flex items-start gap-3 p-3 rounded-xl bg-slate-950/60 border border-slate-800">
              <span className="w-6 h-6 rounded-full bg-cyan-950 border border-cyan-500/40 text-cyan-400 flex items-center justify-center text-xs font-mono font-bold shrink-0 mt-0.5">
                {idx + 1}
              </span>
              <p className="text-xs md:text-sm text-slate-200 font-mono leading-relaxed">
                {step}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Comparative Modal */}
      {compareOpen && (
        <ComparativeModal
          incident={incident}
          allIncidents={allIncidents}
          isOpen={compareOpen}
          onClose={() => setCompareOpen(false)}
        />
      )}

    </div>
  );
};
