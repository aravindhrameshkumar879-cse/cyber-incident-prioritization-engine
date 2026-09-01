import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { 
  SlidersHorizontal, 
  RefreshCw, 
  Sparkles, 
  TrendingUp, 
  TrendingDown, 
  AlertOctagon, 
  Layers, 
  Activity, 
  ShieldAlert, 
  ArrowRight,
  RotateCcw
} from 'lucide-react';
import { SimulationRequest, SimulationResponse, Incident } from '../types';
import { api } from '../services/api';
import { PriorityBadge } from '../components/PriorityBadge';
import { ScoreGauge } from '../components/ScoreGauge';

export const SimulatorPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const incidentIdParam = searchParams.get('incident_id');

  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string>(incidentIdParam || '');
  const [loading, setLoading] = useState(false);
  const [simulation, setSimulation] = useState<SimulationResponse | null>(null);

  // Form State
  const [formData, setFormData] = useState<SimulationRequest>({
    incident_id: incidentIdParam ? Number(incidentIdParam) : undefined,
    title: 'Simulated Outbreak Scenario',
    incident_type: 'Ransomware',
    asset_name: 'CORP-DC-01.local',
    asset_type: 'Domain Controller',
    severity: 85,
    data_sensitivity: 80,
    asset_importance: 95,
    attack_confidence: 90,
    raw_users: 1200,
    raw_systems: 18,
    time_risk: 0.8,
    historical_frequency: 0.7,
    recurrence: 1
  });

  // Load available incidents to populate baseline selector
  useEffect(() => {
    const loadQueue = async () => {
      try {
        const queue = await api.getRankedIncidents(undefined, undefined, 50, 0);
        setIncidents(queue.items);

        if (incidentIdParam) {
          const match = queue.items.find(i => i.id === Number(incidentIdParam));
          if (match) {
            populateFromIncident(match);
          }
        } else if (queue.items.length > 0) {
          // Pre-populate with #1 incident
          populateFromIncident(queue.items[0]);
        }
      } catch (err) {
        console.error(err);
      }
    };
    loadQueue();
  }, [incidentIdParam]);

  const populateFromIncident = (inc: Incident) => {
    setSelectedIncidentId(inc.id.toString());
    setFormData({
      incident_id: inc.id,
      title: inc.title,
      incident_type: inc.incident_type,
      asset_name: inc.asset_name,
      asset_type: inc.asset_type,
      severity: inc.severity,
      data_sensitivity: inc.data_sensitivity,
      asset_importance: inc.asset_importance,
      attack_confidence: inc.attack_confidence,
      raw_users: inc.raw_users,
      raw_systems: inc.raw_systems,
      time_risk: inc.time_risk,
      historical_frequency: inc.historical_frequency,
      recurrence: inc.recurrence
    });
  };

  // Run simulation whenever form changes or recalculate is clicked
  const runSimulation = async (overrideData?: SimulationRequest) => {
    const data = overrideData || formData;
    try {
      setLoading(true);
      const res = await api.simulateScenario(data);
      setSimulation(res);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runSimulation();
  }, [formData.incident_id]);

  const handleIncidentSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setSelectedIncidentId(val);
    if (!val) {
      setFormData(prev => ({ ...prev, incident_id: undefined }));
      return;
    }
    const match = incidents.find(i => i.id === Number(val));
    if (match) {
      populateFromIncident(match);
      runSimulation({
        incident_id: match.id,
        title: match.title,
        incident_type: match.incident_type,
        asset_name: match.asset_name,
        asset_type: match.asset_type,
        severity: match.severity,
        data_sensitivity: match.data_sensitivity,
        asset_importance: match.asset_importance,
        attack_confidence: match.attack_confidence,
        raw_users: match.raw_users,
        raw_systems: match.raw_systems,
        time_risk: match.time_risk,
        historical_frequency: match.historical_frequency,
        recurrence: match.recurrence
      });
    }
  };

  const handleSliderChange = (field: keyof SimulationRequest, val: any) => {
    setFormData(prev => ({ ...prev, [field]: val }));
  };

  const incidentTypes = [
    'Ransomware',
    'Data Exfiltration',
    'Unauthorized Access',
    'DDoS',
    'Phishing',
    'Malware',
    'Insider Threat',
    'Privilege Escalation'
  ];

  const assetTypes = [
    'Domain Controller',
    'Payment Gateway',
    'Database Server',
    'Cloud Storage',
    'Application Server',
    'Workstation',
    'VPN Gateway',
    'Internal Wiki'
  ];

  return (
    <div className="min-h-screen max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="p-1.5 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
              <SlidersHorizontal className="w-5 h-5" />
            </span>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Interactive What-If Simulation Playground
            </h1>
          </div>
          <p className="text-xs font-mono text-slate-400">
            Real-time multi-dimensional risk scoring & queue rank shift evaluation without modifying database state
          </p>
        </div>

        {/* Incident Selector */}
        <div className="flex items-center gap-3">
          <label className="text-xs font-mono text-slate-400 whitespace-nowrap">Load from Queue:</label>
          <select
            value={selectedIncidentId}
            onChange={handleIncidentSelectChange}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs font-mono rounded-xl px-3 py-2 focus:outline-none focus:border-cyan-400"
          >
            <option value="">-- Blank Scenario --</option>
            {incidents.map(inc => (
              <option key={inc.id} value={inc.id}>
                #{inc.priority_rank} [{inc.incident_code}] {inc.title.slice(0, 32)}... ({inc.priority_score.toFixed(1)})
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Controls Column (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <h3 className="text-sm font-mono uppercase tracking-wider text-slate-200 font-bold">
                Contextual Risk Parameter Sliders
              </h3>
              <button
                onClick={() => runSimulation()}
                disabled={loading}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-mono font-bold transition-all shadow-[0_0_12px_rgba(6,182,212,0.3)] disabled:opacity-50"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
                <span>Recalculate Priority</span>
              </button>
            </div>

            {/* Categorical Selectors */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-mono text-slate-400 block mb-1.5">Threat Type</label>
                <select
                  value={formData.incident_type}
                  onChange={(e) => handleSliderChange('incident_type', e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 text-slate-200 rounded-xl px-3 py-2 text-xs font-mono focus:outline-none focus:border-cyan-400"
                >
                  {incidentTypes.map(t => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-xs font-mono text-slate-400 block mb-1.5">Target Infrastructure Tier</label>
                <select
                  value={formData.asset_type}
                  onChange={(e) => handleSliderChange('asset_type', e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 text-slate-200 rounded-xl px-3 py-2 text-xs font-mono focus:outline-none focus:border-cyan-400"
                >
                  {assetTypes.map(a => (
                    <option key={a} value={a}>{a}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Slider: Severity */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300 font-semibold">Technical Alert Severity</span>
                <span className="text-rose-400 font-bold">{formData.severity.toFixed(1)} / 100</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="1"
                value={formData.severity}
                onChange={(e) => handleSliderChange('severity', Number(e.target.value))}
                className="w-full accent-rose-500 cursor-pointer"
              />
            </div>

            {/* Slider: Data Sensitivity */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300 font-semibold">Data Sensitivity</span>
                <span className="text-amber-400 font-bold">{formData.data_sensitivity.toFixed(1)} / 100</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="1"
                value={formData.data_sensitivity}
                onChange={(e) => handleSliderChange('data_sensitivity', Number(e.target.value))}
                className="w-full accent-amber-500 cursor-pointer"
              />
            </div>

            {/* Slider: Asset Importance */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300 font-semibold">Asset Criticality (Host Importance)</span>
                <span className="text-cyan-400 font-bold">{formData.asset_importance.toFixed(1)} / 100</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="1"
                value={formData.asset_importance}
                onChange={(e) => handleSliderChange('asset_importance', Number(e.target.value))}
                className="w-full accent-cyan-500 cursor-pointer"
              />
            </div>

            {/* Slider: Attack Confidence */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300 font-semibold">Attack Confidence (Evidence Certainty)</span>
                <span className="text-emerald-400 font-bold">{formData.attack_confidence.toFixed(1)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="1"
                value={formData.attack_confidence}
                onChange={(e) => handleSliderChange('attack_confidence', Number(e.target.value))}
                className="w-full accent-emerald-500 cursor-pointer"
              />
            </div>

            {/* Impacted Users Slider */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300 font-semibold">Affected User Accounts</span>
                <span className="text-cyan-300 font-bold">{formData.raw_users.toLocaleString()} accounts</span>
              </div>
              <input
                type="range"
                min="1"
                max="10000"
                step="10"
                value={formData.raw_users}
                onChange={(e) => handleSliderChange('raw_users', Number(e.target.value))}
                className="w-full accent-cyan-500 cursor-pointer"
              />
            </div>

            {/* Impacted Systems Slider */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300 font-semibold">Affected Systems / Blast Radius</span>
                <span className="text-purple-300 font-bold">{formData.raw_systems} endpoints</span>
              </div>
              <input
                type="range"
                min="1"
                max="250"
                step="1"
                value={formData.raw_systems}
                onChange={(e) => handleSliderChange('raw_systems', Number(e.target.value))}
                className="w-full accent-purple-500 cursor-pointer"
              />
            </div>

            {/* Off-Hours and Recurrence Toggles */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-xs font-mono text-slate-200 block">Off-Hours / Weekend Multiplier</span>
                  <span className="text-[10px] text-slate-400 font-mono">Elevates risk during off-shift periods</span>
                </div>
                <button
                  type="button"
                  onClick={() => handleSliderChange('time_risk', formData.time_risk >= 0.6 ? 0.2 : 0.85)}
                  className={`w-12 h-6 flex items-center rounded-full p-1 transition-colors ${
                    formData.time_risk >= 0.6 ? 'bg-cyan-500 justify-end' : 'bg-slate-800 justify-start'
                  }`}
                >
                  <span className="w-4 h-4 rounded-full bg-white block shadow-md"></span>
                </button>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-xs font-mono text-slate-200 block">Historical Recurrence Flag</span>
                  <span className="text-[10px] text-slate-400 font-mono">Persistent campaign on this host</span>
                </div>
                <button
                  type="button"
                  onClick={() => handleSliderChange('recurrence', formData.recurrence === 1 ? 0 : 1)}
                  className={`w-12 h-6 flex items-center rounded-full p-1 transition-colors ${
                    formData.recurrence === 1 ? 'bg-rose-500 justify-end' : 'bg-slate-800 justify-start'
                  }`}
                >
                  <span className="w-4 h-4 rounded-full bg-white block shadow-md"></span>
                </button>
              </div>
            </div>

          </div>
        </div>

        {/* Live Simulation Results Column (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {simulation && (
            <div className="p-6 md:p-8 rounded-2xl bg-gradient-to-br from-slate-900 via-[#0d1322] to-slate-900 border-2 border-cyan-500/40 shadow-[0_0_35px_rgba(6,182,212,0.15)] space-y-6">
              
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono uppercase tracking-wider text-cyan-400 font-bold flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4" />
                  Live Simulation Output
                </span>
                <PriorityBadge level={simulation.simulated_priority_level} size="md" />
              </div>

              {/* Main Score Display */}
              <div className="text-center py-4 bg-slate-950/70 rounded-2xl border border-slate-800">
                <span className="text-xs font-mono text-slate-400 block mb-1">
                  PROJECTED HYBRID SCORE
                </span>
                <div className="flex items-baseline justify-center gap-2">
                  <span className="text-5xl font-extrabold font-mono text-white tracking-tight">
                    {simulation.simulated_priority_score.toFixed(1)}
                  </span>
                  <span className="text-sm font-mono text-slate-400">/ 100</span>
                </div>
                <span className="text-xs font-mono text-cyan-400 mt-2 block font-semibold">
                  Band: {simulation.simulated_priority_level}
                </span>
              </div>

              {/* Model Split */}
              <div className="grid grid-cols-2 gap-3 font-mono text-xs">
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">ML Score (65%)</span>
                  <span className="text-lg font-bold text-cyan-300">{simulation.ml_score.toFixed(1)}</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Rule Score (35%)</span>
                  <span className="text-lg font-bold text-purple-300">{simulation.rule_score.toFixed(1)}</span>
                </div>
              </div>

              {/* Rank Shift Indicator */}
              {simulation.baseline_score !== undefined && simulation.baseline_score !== null && (
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2 font-mono text-xs">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Baseline Score:</span>
                    <span className="font-bold text-slate-300">{simulation.baseline_score.toFixed(1)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Score Delta:</span>
                    <span className={`font-bold flex items-center gap-1 ${
                      (simulation.score_delta || 0) >= 0 ? 'text-rose-400' : 'text-emerald-400'
                    }`}>
                      {(simulation.score_delta || 0) >= 0 ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                      {(simulation.score_delta || 0) >= 0 ? `+${simulation.score_delta?.toFixed(1)}` : simulation.score_delta?.toFixed(1)} pts
                    </span>
                  </div>
                  {simulation.estimated_new_rank && (
                    <div className="flex justify-between items-center pt-2 border-t border-slate-800/80">
                      <span className="text-slate-400">Estimated Queue Rank:</span>
                      <span className="font-bold text-cyan-400">
                        #{simulation.estimated_new_rank}
                        {simulation.estimated_rank_shift ? ` (${simulation.estimated_rank_shift > 0 ? `+${simulation.estimated_rank_shift}` : simulation.estimated_rank_shift} spots)` : ''}
                      </span>
                    </div>
                  )}
                </div>
              )}

              {/* Explainability Paragraph */}
              <div className="p-4 rounded-xl bg-cyan-950/20 border border-cyan-500/30">
                <h4 className="text-[11px] font-mono uppercase tracking-wider text-cyan-300 font-semibold mb-1">
                  Simulation Context Synthesis
                </h4>
                <p className="text-xs text-slate-200 font-mono leading-relaxed">
                  {simulation.explainability_summary}
                </p>
              </div>

              {/* Prescribed Containment Steps */}
              <div className="space-y-2">
                <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">
                  Recommended Remediation Vector
                </h4>
                <ul className="space-y-1 text-xs font-mono text-slate-300">
                  {simulation.mitigation_recommendations.slice(0, 3).map((s, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-cyan-400">&bull;</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>

            </div>
          )}
        </div>

      </div>

    </div>
  );
};
