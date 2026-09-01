import React, { useState, useEffect } from 'react';
import { 
  Cpu, 
  CheckCircle2, 
  Layers, 
  BarChart2, 
  Award, 
  Activity, 
  ShieldCheck, 
  BookOpen, 
  RefreshCw 
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';
import { ModelPerformance } from '../types';
import { api } from '../services/api';

export const ModelAdminPage: React.FC = () => {
  const [modelData, setModelData] = useState<ModelPerformance | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchModelMetrics = async () => {
    try {
      setLoading(true);
      const res = await api.getModelPerformance();
      setModelData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModelMetrics();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center font-mono text-slate-400">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p>Inspecting ML model weights and evaluation artifacts...</p>
        </div>
      </div>
    );
  }

  if (!modelData) {
    return (
      <div className="min-h-screen flex items-center justify-center font-mono text-slate-400">
        <p>Model metadata unavailable.</p>
      </div>
    );
  }

  const { metrics, feature_importances } = modelData;

  return (
    <div className="min-h-screen max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="p-1.5 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
              <Cpu className="w-5 h-5" />
            </span>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Machine Learning Engine & Model Architecture
            </h1>
          </div>
          <p className="text-xs font-mono text-slate-400">
            Calibrated Gradient Boosting Regressor trained across 55,000+ multi-dimensional cybersecurity incident scenarios
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 px-3 py-1 text-xs font-mono rounded-full bg-emerald-950/80 border border-emerald-500/50 text-emerald-300">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            MODEL ACTIVE &amp; CALIBRATED
          </span>
        </div>
      </div>

      {/* Evaluation KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 font-mono">
        <div className="p-5 rounded-2xl bg-slate-900 border border-cyan-500/30">
          <span className="text-xs text-cyan-400 block mb-1">R² Goodness of Fit</span>
          <span className="text-3xl font-extrabold text-white">{metrics.r2_score.toFixed(4)}</span>
          <span className="text-[10px] text-slate-400 block mt-1">High predictive variance capture</span>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
          <span className="text-xs text-slate-400 block mb-1">Root Mean Sq. Error (RMSE)</span>
          <span className="text-3xl font-extrabold text-white">{metrics.rmse.toFixed(3)}</span>
          <span className="text-[10px] text-slate-400 block mt-1">Score scale: 0 - 100</span>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
          <span className="text-xs text-slate-400 block mb-1">Mean Absolute Error (MAE)</span>
          <span className="text-3xl font-extrabold text-white">{metrics.mae.toFixed(3)}</span>
          <span className="text-[10px] text-slate-400 block mt-1">Median deviation per prediction</span>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
          <span className="text-xs text-slate-400 block mb-1">Synthetic Dataset</span>
          <span className="text-3xl font-extrabold text-white">{metrics.dataset_samples.toLocaleString()}</span>
          <span className="text-[10px] text-slate-400 block mt-1">80/20 train/test split</span>
        </div>
      </div>

      {/* Feature Importance Horizontal Bar Chart */}
      <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-mono uppercase tracking-wider text-white font-bold flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-cyan-400" />
              12 Contextual Features: Permutation Importance Ranking
            </h3>
            <p className="text-xs font-mono text-slate-400 mt-1">
              Relative contribution weight of each normalized dimension in the regression model
            </p>
          </div>
          <span className="text-xs font-mono text-cyan-400">Sum = 100%</span>
        </div>

        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={feature_importances} layout="vertical" margin={{ left: 40, right: 30, top: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11, fill: '#94a3b8' }} unit="%" />
              <YAxis dataKey="feature" type="category" stroke="#64748b" tick={{ fontSize: 11, fill: '#cbd5e1' }} width={180} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                formatter={(value: any) => [`${value}%`, 'Importance']}
              />
              <Bar dataKey="percentage" fill="#06b6d4" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Hybrid Prioritization Formula Architecture */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Formula Box */}
        <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4 font-mono text-xs">
          <h3 className="text-sm uppercase tracking-wider text-white font-bold flex items-center gap-2">
            <Layers className="w-4 h-4 text-purple-400" />
            Hybrid Prioritization Formula
          </h3>

          <div className="p-4 rounded-xl bg-slate-950 border border-purple-500/30 text-slate-200">
            <span className="text-cyan-400 font-bold block mb-1">Composite Priority Score Formula:</span>
            <p className="text-base font-bold text-white">
              S = 0.65 &times; S<sub>ML</sub> + 0.35 &times; S<sub>Rule</sub>
            </p>
          </div>

          <div className="space-y-2 text-slate-300">
            <p><strong className="text-cyan-400">65% Machine Learning Model:</strong> Evaluates multi-dimensional nonlinear risk across 12 standardized contextual factors.</p>
            <p><strong className="text-purple-400">35% Deterministic Rule Engine:</strong> Enforces business policy boosts (Tier-0 assets +15, Crown jewels +10, Ransomware/Exfil +12, Off-hours multiplier 1.15x, Historical recurrence +8).</p>
          </div>

          <div className="pt-2 border-t border-slate-800">
            <span className="text-slate-400 block mb-1">Priority Bands:</span>
            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div className="p-2 rounded bg-rose-950/40 text-rose-300 border border-rose-500/30">CRITICAL: &ge; 80.0</div>
              <div className="p-2 rounded bg-amber-950/40 text-amber-300 border border-amber-500/30">HIGH: 60.0 - 79.9</div>
              <div className="p-2 rounded bg-yellow-950/40 text-yellow-300 border border-yellow-500/30">MEDIUM: 30.0 - 59.9</div>
              <div className="p-2 rounded bg-emerald-950/40 text-emerald-300 border border-emerald-500/30">LOW: &lt; 30.0</div>
            </div>
          </div>
        </div>

        {/* Deterministic Tie-Breaker Box */}
        <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4 font-mono text-xs">
          <h3 className="text-sm uppercase tracking-wider text-white font-bold flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-cyan-400" />
            Deterministic 5-Tier Tie-Breaking Hierarchy
          </h3>

          <p className="text-slate-400 leading-relaxed">
            To eliminate triage ambiguity when two incidents have identical composite priority scores, the engine applies strict deterministic sorting:
          </p>

          <ol className="space-y-2 text-slate-200">
            <li className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-cyan-950 text-cyan-400 flex items-center justify-center font-bold">1</span>
              <span><strong>priority_score</strong> (Descending)</span>
            </li>
            <li className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-400 flex items-center justify-center font-bold">2</span>
              <span><strong>business_impact</strong> (Descending)</span>
            </li>
            <li className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-400 flex items-center justify-center font-bold">3</span>
              <span><strong>asset_importance</strong> (Descending)</span>
            </li>
            <li className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-400 flex items-center justify-center font-bold">4</span>
              <span><strong>attack_confidence</strong> (Descending)</span>
            </li>
            <li className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-400 flex items-center justify-center font-bold">5</span>
              <span><strong>detected_at</strong> (Ascending - oldest uncontained first)</span>
            </li>
          </ol>
        </div>

      </div>

    </div>
  );
};
