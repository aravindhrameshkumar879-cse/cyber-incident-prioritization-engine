import React from 'react';
import { IncidentStatus } from '../types';

interface StatusBadgeProps {
  status: IncidentStatus;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const styles: Record<IncidentStatus, string> = {
    new: 'bg-cyan-950/60 border-cyan-500/40 text-cyan-300',
    investigating: 'bg-purple-950/60 border-purple-500/40 text-purple-300',
    contained: 'bg-amber-950/60 border-amber-500/40 text-amber-300',
    resolved: 'bg-slate-800/80 border-slate-600/40 text-slate-400'
  };

  const labels: Record<IncidentStatus, string> = {
    new: 'NEW ALERT',
    investigating: 'UNDER INVESTIGATION',
    contained: 'CONTAINED',
    resolved: 'RESOLVED'
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono uppercase tracking-wider border ${styles[status] || styles.new}`}>
      {labels[status] || status}
    </span>
  );
};
