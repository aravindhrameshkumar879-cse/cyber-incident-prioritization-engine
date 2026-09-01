import React, { useState, useEffect } from 'react';
import { X, ArrowRightLeft, Sparkles, Scale, TrendingUp, TrendingDown, ArrowRight } from 'lucide-react';
import { Incident, IncidentComparisonResponse } from '../types';
import { api } from '../services/api';
import { PriorityBadge } from './PriorityBadge';

interface ComparativeModalProps {
  incident: Incident;
  allIncidents: Incident[];
  isOpen: boolean;
  onClose: () => void;
}

export const ComparativeModal: React.FC<ComparativeModalProps> = ({
  incident,
  allIncidents,
  isOpen,
  onClose
}) => {
  const [targetId, setTargetId] = useState<number | ''>('');
  const [loading, setLoading] = useState(false);
  const [comparison, setComparison] = useState<IncidentComparisonResponse | null>(null);

  // Filter out the current incident
  const candidateIncidents = allIncidents.filter(i => i.id !== incident.id);

  useEffect(() => {
    if (candidateIncidents.length > 0 && !targetId) {
      // Default to the next ranked or first available candidate
      setTargetId(candidateIncidents[0].id);
    }
  }, [candidateIncidents, targetId]);

  useEffect(() => {
    if (isOpen && targetId) {
      fetchComparison(Number(targetId));
    }
  }, [isOpen, targetId]);

  const fetchComparison = async (otherId: number) => {
    try {
      setLoading(true);
      const res = await api.compareIncidents(incident.id, otherId);
      setComparison(res);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-4xl max-h-[92vh] overflow-y-auto rounded-2xl bg-[#0d1322] border border-slate-700 shadow-2xl p-6 md:p-8 text-slate-100">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2.5 rounded-xl bg-purple-500/20 text-purple-400 border border-purple-500/30">
            <Scale className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              Comparative Prioritization Engine
            </h2>
            <p className="text-xs text-slate-400 font-mono">
              Algorithmic Side-by-Side Factor Analysis & Plain-Language Justification
            </p>
          </div>
        </div>

        {/* Select Comparison Target */}
        <div className="mb-6 p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="text-xs font-mono">
            <span className="text-slate-400 block mb-0.5">COMPARING CURRENT INCIDENT:</span>
            <strong className="text-cyan-400 text-sm">{incident.incident_code}</strong>: {incident.title}
          </div>
          
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <label className="text-xs font-mono text-slate-400 whitespace-nowrap">Against:</label>
            <select
              value={targetId}
              onChange={(e) => setTargetId(Number(e.target.value))}
              className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-400 w-full sm:w-64"
            >
              {candidateIncidents.map(c => (
                <option key={c.id} value={c.id}>
                  #{c.priority_rank} [{c.incident_code}] {c.incident_type} ({c.priority_score.toFixed(1)})
                </option>
              ))}
            </select>
          </div>
        </div>

        {loading && (
          <div className="py-12 text-center text-xs font-mono text-slate-400">
            <div className="inline-block w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mb-3"></div>
            <p>Evaluating multi-dimensional divergence across 12 features...</p>
          </div>
        )}

        {!loading && comparison && (
          <div className="space-y-6">
            {/* Side-by-side Score Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Incident A */}
              <div className={`p-5 rounded-xl border ${
                comparison.higher_priority_code === comparison.incident_a.incident_code
                  ? 'bg-slate-900/90 border-cyan-500/50 shadow-[0_0_20px_rgba(6,182,212,0.15)]'
                  : 'bg-slate-950/80 border-slate-800'
              }`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-xs font-bold text-cyan-400">{comparison.incident_a.incident_code}</span>
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-mono text-slate-400">Rank #{comparison.incident_a.priority_rank}</span>
                    <PriorityBadge level={comparison.incident_a.priority_level} size="sm" />
                  </div>
                </div>
                <h4 className="font-semibold text-sm text-white mb-2 line-clamp-1">{comparison.incident_a.title}</h4>
                <div className="flex items-baseline gap-2 mb-3">
                  <span className="text-3xl font-extrabold font-mono text-white">
                    {comparison.incident_a.priority_score.toFixed(1)}
                  </span>
                  <span className="text-xs text-slate-400 font-mono">/ 100</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-slate-300">
                  <div className="p-2 rounded bg-slate-850/60">
                    <span className="text-slate-400 block text-[10px]">ML Score (65%)</span>
                    <span className="text-cyan-300 font-bold">{comparison.incident_a.ml_score.toFixed(1)}</span>
                  </div>
                  <div className="p-2 rounded bg-slate-850/60">
                    <span className="text-slate-400 block text-[10px]">Rule Score (35%)</span>
                    <span className="text-purple-300 font-bold">{comparison.incident_a.rule_score.toFixed(1)}</span>
                  </div>
                </div>
              </div>

              {/* Incident B */}
              <div className={`p-5 rounded-xl border ${
                comparison.higher_priority_code === comparison.incident_b.incident_code
                  ? 'bg-slate-900/90 border-cyan-500/50 shadow-[0_0_20px_rgba(6,182,212,0.15)]'
                  : 'bg-slate-950/80 border-slate-800'
              }`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-xs font-bold text-slate-300">{comparison.incident_b.incident_code}</span>
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-mono text-slate-400">Rank #{comparison.incident_b.priority_rank}</span>
                    <PriorityBadge level={comparison.incident_b.priority_level} size="sm" />
                  </div>
                </div>
                <h4 className="font-semibold text-sm text-white mb-2 line-clamp-1">{comparison.incident_b.title}</h4>
                <div className="flex items-baseline gap-2 mb-3">
                  <span className="text-3xl font-extrabold font-mono text-white">
                    {comparison.incident_b.priority_score.toFixed(1)}
                  </span>
                  <span className="text-xs text-slate-400 font-mono">/ 100</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-slate-300">
                  <div className="p-2 rounded bg-slate-850/60">
                    <span className="text-slate-400 block text-[10px]">ML Score (65%)</span>
                    <span className="text-cyan-300 font-bold">{comparison.incident_b.ml_score.toFixed(1)}</span>
                  </div>
                  <div className="p-2 rounded bg-slate-850/60">
                    <span className="text-slate-400 block text-[10px]">Rule Score (35%)</span>
                    <span className="text-purple-300 font-bold">{comparison.incident_b.rule_score.toFixed(1)}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Plain-Language Justification */}
            <div className="p-4 rounded-xl bg-gradient-to-r from-purple-950/30 via-slate-900 to-cyan-950/30 border border-purple-500/40">
              <div className="flex items-start gap-3">
                <Sparkles className="w-5 h-5 text-purple-400 mt-0.5 shrink-0" />
                <div>
                  <h4 className="text-xs font-mono uppercase tracking-wider text-purple-300 font-semibold mb-1">
                    Comparative Ranking Rationale
                  </h4>
                  <p className="text-sm text-slate-200 leading-relaxed">
                    {comparison.plain_language_justification}
                  </p>
                </div>
              </div>
            </div>

            {/* Divergent Factors Table */}
            <div>
              <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold mb-3">
                Primary Divergence Factors
              </h4>
              <div className="overflow-x-auto rounded-xl border border-slate-800">
                <table className="w-full text-xs font-mono text-left">
                  <thead className="bg-slate-900 text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="px-4 py-2.5">Feature Factor</th>
                      <th className="px-4 py-2.5">{comparison.incident_a.incident_code}</th>
                      <th className="px-4 py-2.5">{comparison.incident_b.incident_code}</th>
                      <th className="px-4 py-2.5">Delta</th>
                      <th className="px-4 py-2.5">Favors Priority</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 bg-slate-950/40">
                    {comparison.divergent_factors.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-4 py-4 text-center text-slate-500">
                          Identical or near-identical factor scores across all dimensions.
                        </td>
                      </tr>
                    ) : (
                      comparison.divergent_factors.map((df, idx) => (
                        <tr key={idx} className="hover:bg-slate-900/50">
                          <td className="px-4 py-2.5 font-semibold text-slate-200">{df.label}</td>
                          <td className="px-4 py-2.5 text-cyan-300">{df.val_a}</td>
                          <td className="px-4 py-2.5 text-slate-300">{df.val_b}</td>
                          <td className="px-4 py-2.5 font-bold text-white">
                            {df.diff > 0 ? `+${df.diff}` : df.diff}
                          </td>
                          <td className="px-4 py-2.5">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              df.favors === comparison.incident_a.incident_code
                                ? 'bg-cyan-950 text-cyan-300 border border-cyan-500/40'
                                : 'bg-slate-800 text-slate-300 border border-slate-700'
                            }`}>
                              {df.favors}
                            </span>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        )}

      </div>
    </div>
  );
};
