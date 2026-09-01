import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  PieChart, 
  TrendingUp, 
  ShieldAlert, 
  Server, 
  Flame, 
  Activity, 
  RefreshCw 
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  AreaChart, 
  Area 
} from 'recharts';
import { AnalyticsSummary } from '../types';
import { api } from '../services/api';

export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const res = await api.getAnalytics();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center font-mono text-slate-400">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p>Aggregating cyber telemetry across incident database...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center font-mono text-slate-400">
        <p>No analytics data available. Load demo incidents from Dashboard.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="p-1.5 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
              <BarChart3 className="w-5 h-5" />
            </span>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              SOC Analytics & Triage Intelligence
            </h1>
          </div>
          <p className="text-xs font-mono text-slate-400">
            Real-time multi-dimensional aggregations across threat vectors, severities, and target infrastructure
          </p>
        </div>

        <button
          onClick={fetchAnalytics}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-850 hover:bg-slate-800 text-slate-200 border border-slate-700 text-xs font-mono transition-colors"
        >
          <RefreshCw className="w-4 h-4 text-cyan-400" />
          <span>Refresh Analytics</span>
        </button>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 font-mono">
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
          <span className="text-xs text-slate-400 block mb-1">Total Ingested</span>
          <span className="text-3xl font-extrabold text-white">{data.total_incidents}</span>
          <span className="text-[10px] text-cyan-400 block mt-1">{data.active_incidents} active in queue</span>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-rose-500/30">
          <span className="text-xs text-rose-400 block mb-1">Critical Tier (&ge; 80)</span>
          <span className="text-3xl font-extrabold text-white">{data.critical_count}</span>
          <span className="text-[10px] text-rose-400 block mt-1">High-urgency response</span>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-amber-500/30">
          <span className="text-xs text-amber-400 block mb-1">High Tier (60 - 79)</span>
          <span className="text-3xl font-extrabold text-white">{data.high_count}</span>
          <span className="text-[10px] text-amber-400 block mt-1">Tier-2 triage required</span>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-cyan-500/30">
          <span className="text-xs text-cyan-400 block mb-1">Mean Priority Score</span>
          <span className="text-3xl font-extrabold text-white">{data.mean_priority_score.toFixed(1)}</span>
          <span className="text-[10px] text-slate-400 block mt-1">ML Mean: {data.mean_ml_score.toFixed(1)}</span>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Threat Category Distribution */}
        <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-mono uppercase tracking-wider text-white font-bold flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-cyan-400" />
              Incidents by Threat Vector
            </h3>
            <span className="text-xs font-mono text-slate-400">Total volume</span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.type_distribution} layout="vertical" margin={{ left: 20, right: 20, top: 10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <YAxis dataKey="name" type="category" stroke="#64748b" tick={{ fontSize: 11, fill: '#cbd5e1' }} width={120} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#06b6d4" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Technical Severity Distribution */}
        <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-mono uppercase tracking-wider text-white font-bold flex items-center gap-2">
              <Flame className="w-4 h-4 text-rose-400" />
              Technical Severity Buckets
            </h3>
            <span className="text-xs font-mono text-slate-400">0 - 100 Scale</span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.severity_distribution} margin={{ left: 10, right: 10, top: 10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="range" stroke="#64748b" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#f43f5e" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Affected Critical Assets */}
        <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-mono uppercase tracking-wider text-white font-bold flex items-center gap-2">
              <Server className="w-4 h-4 text-purple-400" />
              Top Targeted Infrastructure Assets
            </h3>
            <span className="text-xs font-mono text-slate-400">By alert frequency</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs font-mono text-left">
              <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="px-3 py-2">Asset Name</th>
                  <th className="px-3 py-2">Type</th>
                  <th className="px-3 py-2">Incidents</th>
                  <th className="px-3 py-2">Max Priority</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {data.top_affected_assets.map((a, idx) => (
                  <tr key={idx} className="hover:bg-slate-850">
                    <td className="px-3 py-2.5 font-semibold text-white">{a.asset_name}</td>
                    <td className="px-3 py-2.5 text-slate-400">{a.asset_type}</td>
                    <td className="px-3 py-2.5 text-cyan-400 font-bold">{a.incident_count}</td>
                    <td className="px-3 py-2.5 font-bold text-rose-400">{a.max_priority.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Temporal Detection Trend */}
        <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-mono uppercase tracking-wider text-white font-bold flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-emerald-400" />
              Incident Ingestion Timeline
            </h3>
            <span className="text-xs font-mono text-slate-400">Recent volume</span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.recent_trend} margin={{ left: 10, right: 10, top: 10, bottom: 10 }}>
                <defs>
                  <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="total" stroke="#10b981" fillOpacity={1} fill="url(#colorTotal)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

    </div>
  );
};
