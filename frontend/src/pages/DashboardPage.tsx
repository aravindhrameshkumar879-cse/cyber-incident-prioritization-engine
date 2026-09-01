import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ShieldAlert, 
  Search, 
  SlidersHorizontal, 
  FileText, 
  ExternalLink, 
  RefreshCw, 
  Sparkles, 
  Flame, 
  Activity, 
  AlertTriangle, 
  CheckCircle2, 
  ArrowUpDown,
  Filter,
  Layers,
  Clock,
  ArrowRight
} from 'lucide-react';
import { Incident, IncidentStatus } from '../types';
import { api } from '../services/api';
import { PriorityBadge } from '../components/PriorityBadge';
import { StatusBadge } from '../components/StatusBadge';
import { ScoreGauge } from '../components/ScoreGauge';
import { WhyNumberOneModal } from '../components/WhyNumberOneModal';
import { ComparativeModal } from '../components/ComparativeModal';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [topIncident, setTopIncident] = useState<Incident | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [seedingDemo, setSeedingDemo] = useState(false);

  // Modals state
  const [whyNumberOneOpen, setWhyNumberOneOpen] = useState(false);
  const [compareIncident, setCompareIncident] = useState<Incident | null>(null);
  const [reportNotification, setReportNotification] = useState<string | null>(null);

  const fetchIncidents = async () => {
    try {
      setLoading(true);
      const res = await api.getRankedIncidents(statusFilter, searchQuery, 50, 0);
      setIncidents(res.items);
      setTotalCount(res.total);
      if (res.top_incident) {
        setTopIncident(res.top_incident);
      } else if (res.items.length > 0) {
        setTopIncident(res.items[0]);
      } else {
        setTopIncident(null);
      }
    } catch (err: any) {
      console.error('Error fetching incidents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, [statusFilter, searchQuery]);

  const handleSeedDemo = async () => {
    try {
      setSeedingDemo(true);
      const res = await api.loadDemoData();
      await fetchIncidents();
      setReportNotification(`Ingested and scored 100 demo incidents into the active queue.`);
      setTimeout(() => setReportNotification(null), 5000);
    } catch (err: any) {
      alert(`Error loading demo incidents: ${err.message}`);
    } finally {
      setSeedingDemo(false);
    }
  };

  const handleGenerateReport = async (incidentId: number) => {
    try {
      setReportNotification('Generating ReportLab PDF dossier...');
      const rep = await api.generateReport(incidentId, 'executive');
      setReportNotification(`Report generated! Initiating download...`);
      // Trigger download
      window.open(rep.download_url, '_blank');
      setTimeout(() => setReportNotification(null), 4000);
    } catch (err: any) {
      alert(`Error generating PDF: ${err.message}`);
    }
  };

  // Quick stats calculation
  const criticalCount = incidents.filter(i => i.priority_level === 'CRITICAL').length;
  const highCount = incidents.filter(i => i.priority_level === 'HIGH').length;
  const activeCount = incidents.filter(i => i.status === 'new' || i.status === 'investigating').length;
  const avgScore = incidents.length > 0
    ? (incidents.reduce((acc, i) => acc + i.priority_score, 0) / incidents.length).toFixed(1)
    : '0.0';

  return (
    <div className="min-h-screen max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Toast Notification */}
      {reportNotification && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900/95 border border-cyan-500/50 text-cyan-300 text-xs font-mono shadow-[0_0_20px_rgba(6,182,212,0.3)] animate-slide-up">
          <CheckCircle2 className="w-4 h-4 text-cyan-400" />
          <span>{reportNotification}</span>
        </div>
      )}

      {/* Top Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-gradient-to-br from-rose-950/40 to-slate-900 border border-rose-500/30 shadow-[0_0_25px_rgba(244,63,94,0.12)] flex items-center justify-between">
          <div>
            <span className="text-xs font-mono uppercase tracking-wider text-rose-400 font-semibold block mb-1">
              Critical Threats
            </span>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold font-mono text-white">{criticalCount}</span>
              <span className="text-xs text-rose-400 font-mono">Score &ge; 80</span>
            </div>
          </div>
          <div className="p-3 rounded-xl bg-rose-500/20 text-rose-400">
            <Flame className="w-6 h-6 animate-pulse" />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-gradient-to-br from-cyan-950/40 to-slate-900 border border-cyan-500/30 shadow-[0_0_25px_rgba(6,182,212,0.12)] flex items-center justify-between">
          <div>
            <span className="text-xs font-mono uppercase tracking-wider text-cyan-400 font-semibold block mb-1">
              Active Triage Queue
            </span>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold font-mono text-white">{activeCount}</span>
              <span className="text-xs text-slate-400 font-mono">of {totalCount} total</span>
            </div>
          </div>
          <div className="p-3 rounded-xl bg-cyan-500/20 text-cyan-400">
            <Activity className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-gradient-to-br from-amber-950/40 to-slate-900 border border-amber-500/30 flex items-center justify-between">
          <div>
            <span className="text-xs font-mono uppercase tracking-wider text-amber-400 font-semibold block mb-1">
              Mean Risk Score
            </span>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold font-mono text-white">{avgScore}</span>
              <span className="text-xs text-amber-400 font-mono">/ 100</span>
            </div>
          </div>
          <div className="p-3 rounded-xl bg-amber-500/20 text-amber-400">
            <Layers className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-gradient-to-br from-purple-950/40 to-slate-900 border border-purple-500/30 flex items-center justify-between">
          <div>
            <span className="text-xs font-mono uppercase tracking-wider text-purple-400 font-semibold block mb-1">
              Prioritization Engine
            </span>
            <div className="text-xs font-mono text-slate-300">
              <strong className="text-cyan-400">65%</strong> ML Regressor + <strong className="text-purple-400">35%</strong> Rules
            </div>
            <span className="text-[10px] text-slate-400 font-mono mt-1 block">Deterministic Tie-Breaking</span>
          </div>
          <div className="p-3 rounded-xl bg-purple-500/20 text-purple-400">
            <SlidersHorizontal className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* TOP RANKED INCIDENT SPOTLIGHT CARD */}
      {topIncident && (
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-rose-950/60 via-slate-900 to-[#0d1322] border-2 border-rose-500/60 shadow-[0_0_35px_rgba(244,63,94,0.2)] p-6 md:p-8">
          <div className="absolute -top-12 -right-12 w-56 h-56 bg-rose-500/10 rounded-full blur-3xl pointer-events-none" />
          
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6 relative z-10">
            <div className="space-y-3 max-w-3xl">
              <div className="flex flex-wrap items-center gap-3">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-500 text-black text-xs font-mono font-bold tracking-wider shadow-[0_0_15px_rgba(244,63,94,0.6)]">
                  <Flame className="w-3.5 h-3.5" />
                  PRIORITY #1 SPOTLIGHT
                </span>
                <PriorityBadge level={topIncident.priority_level} score={topIncident.priority_score} size="md" />
                <StatusBadge status={topIncident.status} />
                <span className="text-xs font-mono text-slate-400">
                  Detected {new Date(topIncident.detected_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} UTC
                </span>
              </div>

              <div>
                <h3 className="text-xl md:text-2xl font-extrabold text-white tracking-tight">
                  {topIncident.title}
                </h3>
                <p className="text-xs md:text-sm text-slate-300 font-mono mt-1">
                  Target Asset: <strong className="text-cyan-400">{topIncident.asset_name}</strong> ({topIncident.asset_type}) &bull; Threat: <strong className="text-white">{topIncident.incident_type}</strong>
                </p>
              </div>

              {topIncident.why_number_one && (
                <p className="text-xs md:text-sm text-slate-200 bg-slate-900/80 border border-slate-700/60 p-3.5 rounded-xl leading-relaxed">
                  <strong className="text-rose-400 font-mono uppercase text-[11px] block mb-1">Executive Triage Rationale:</strong>
                  {topIncident.why_number_one}
                </p>
              )}
            </div>

            {/* Right: Score Gauge & WHY #1 Action Button */}
            <div className="flex flex-col sm:flex-row lg:flex-col items-start lg:items-end justify-between gap-4 border-t lg:border-t-0 lg:border-l border-slate-800 pt-4 lg:pt-0 lg:pl-6 shrink-0">
              <ScoreGauge
                score={topIncident.priority_score}
                mlScore={topIncident.ml_score}
                ruleScore={topIncident.rule_score}
                level={topIncident.priority_level}
                size="lg"
              />

              <div className="flex items-center gap-3 w-full sm:w-auto">
                {/* THE WHY #1? BUTTON */}
                <button
                  onClick={() => setWhyNumberOneOpen(true)}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-rose-500 hover:bg-rose-400 text-black font-mono font-bold text-xs shadow-[0_0_20px_rgba(244,63,94,0.5)] transition-all hover:scale-105 active:scale-95"
                >
                  <Sparkles className="w-4 h-4" />
                  <span>WHY #1?</span>
                </button>

                <button
                  onClick={() => navigate(`/incidents/${topIncident.id}`)}
                  className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-mono text-xs border border-slate-700 transition-colors"
                >
                  <span>Investigate</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Search & Filter Toolbar */}
      <div className="p-4 rounded-2xl bg-[#0f172a]/90 border border-slate-800 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Filter by code (INC-...), host, threat vector, or asset..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 font-mono"
          />
        </div>

        {/* Status Filter Tabs */}
        <div className="flex flex-wrap items-center gap-1.5 font-mono text-xs">
          {['all', 'new', 'investigating', 'contained', 'resolved'].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-3 py-1.5 rounded-lg capitalize transition-all ${
                statusFilter === status
                  ? 'bg-cyan-500 text-black font-bold shadow-[0_0_12px_rgba(6,182,212,0.3)]'
                  : 'bg-slate-850 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              {status}
            </button>
          ))}
        </div>

        {/* Refresh button */}
        <button
          onClick={fetchIncidents}
          className="p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-800 transition-colors"
          title="Refresh Queue"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Ranked Queue Table */}
      <div className="overflow-hidden rounded-2xl border border-slate-800 bg-[#0c1220]/90 shadow-xl">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h4 className="font-bold text-white text-sm tracking-tight flex items-center gap-2">
              <span>PRIORITIZED INCIDENT QUEUE</span>
              <span className="text-xs font-mono text-cyan-400">({totalCount} Incidents)</span>
            </h4>
          </div>
          <span className="text-[11px] font-mono text-slate-400 hidden sm:inline">
            Sorted by 5-Tier Deterministic Tie-Breaker
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-900/90 text-[11px] font-mono uppercase tracking-wider text-slate-400 border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Rank</th>
                <th className="px-4 py-3">Code</th>
                <th className="px-4 py-3">Threat Profile</th>
                <th className="px-4 py-3">Target Asset</th>
                <th className="px-4 py-3">Severity</th>
                <th className="px-4 py-3">Score & Split</th>
                <th className="px-4 py-3">Priority Level</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-850 text-xs font-mono">
              {loading ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400">
                    <div className="inline-block w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mb-3"></div>
                    <p>Scoring and evaluating prioritization queue...</p>
                  </td>
                </tr>
              ) : incidents.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-500">
                    <p className="mb-2">No incidents found matching criteria.</p>
                    <button
                      onClick={handleSeedDemo}
                      disabled={seedingDemo}
                      className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-bold"
                    >
                      <RefreshCw className={`w-4 h-4 ${seedingDemo ? 'animate-spin' : ''}`} />
                      Load 100 Demo Incidents
                    </button>
                  </td>
                </tr>
              ) : (
                incidents.map((inc) => (
                  <tr 
                    key={inc.id}
                    className={`hover:bg-slate-850/60 transition-colors ${
                      inc.priority_rank === 1 ? 'bg-rose-950/15' : ''
                    }`}
                  >
                    {/* Rank */}
                    <td className="px-4 py-3 font-bold">
                      <span className={`inline-flex items-center justify-center w-7 h-7 rounded-lg text-xs font-mono ${
                        inc.priority_rank === 1
                          ? 'bg-rose-500 text-black font-extrabold shadow-[0_0_10px_rgba(244,63,94,0.5)]'
                          : inc.priority_rank <= 3
                          ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                          : 'bg-slate-800 text-slate-400'
                      }`}>
                        #{inc.priority_rank}
                      </span>
                    </td>

                    {/* Code */}
                    <td className="px-4 py-3 font-semibold text-cyan-400">
                      {inc.incident_code}
                    </td>

                    {/* Threat Profile */}
                    <td className="px-4 py-3 max-w-xs">
                      <span className="font-semibold text-white block truncate">{inc.title}</span>
                      <span className="text-[10px] text-slate-400 block">{inc.incident_type}</span>
                    </td>

                    {/* Target Asset */}
                    <td className="px-4 py-3">
                      <span className="text-slate-200 block truncate">{inc.asset_name}</span>
                      <span className="text-[10px] text-slate-500 block">{inc.asset_type}</span>
                    </td>

                    {/* Severity */}
                    <td className="px-4 py-3 font-semibold">
                      <span className={inc.severity >= 75 ? 'text-rose-400' : inc.severity >= 50 ? 'text-amber-400' : 'text-slate-300'}>
                        {inc.severity.toFixed(1)}
                      </span>
                    </td>

                    {/* Score & Split */}
                    <td className="px-4 py-3">
                      <ScoreGauge
                        score={inc.priority_score}
                        mlScore={inc.ml_score}
                        ruleScore={inc.rule_score}
                        level={inc.priority_level}
                        size="sm"
                      />
                    </td>

                    {/* Priority Level */}
                    <td className="px-4 py-3">
                      <PriorityBadge level={inc.priority_level} size="sm" />
                    </td>

                    {/* Status */}
                    <td className="px-4 py-3">
                      <StatusBadge status={inc.status} />
                    </td>

                    {/* Actions */}
                    <td className="px-4 py-3 text-right space-x-1">
                      {inc.priority_rank === 1 && (
                        <button
                          onClick={() => setWhyNumberOneOpen(true)}
                          className="px-2 py-1 rounded bg-rose-500/20 hover:bg-rose-500/40 text-rose-300 border border-rose-500/40 text-[11px] font-bold"
                          title="Explain why this incident is #1"
                        >
                          Why #1?
                        </button>
                      )}

                      <button
                        onClick={() => setCompareIncident(inc)}
                        className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-[11px]"
                        title="Compare with another incident"
                      >
                        Compare
                      </button>

                      <button
                        onClick={() => handleGenerateReport(inc.id)}
                        className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-cyan-400"
                        title="Download PDF Report"
                      >
                        <FileText className="w-4 h-4 inline" />
                      </button>

                      <button
                        onClick={() => navigate(`/incidents/${inc.id}`)}
                        className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white"
                        title="View Full Incident Detail"
                      >
                        <ExternalLink className="w-4 h-4 inline" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* WHY #1 MODAL */}
      <WhyNumberOneModal
        incident={topIncident}
        isOpen={whyNumberOneOpen}
        onClose={() => setWhyNumberOneOpen(false)}
        onGenerateReport={handleGenerateReport}
      />

      {/* COMPARATIVE MODAL */}
      {compareIncident && (
        <ComparativeModal
          incident={compareIncident}
          allIncidents={incidents}
          isOpen={!!compareIncident}
          onClose={() => setCompareIncident(null)}
        />
      )}

    </div>
  );
};
