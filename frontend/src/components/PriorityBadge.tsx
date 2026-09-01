import React from 'react';
import { PriorityLevel } from '../types';

interface PriorityBadgeProps {
  level: PriorityLevel;
  size?: 'sm' | 'md' | 'lg';
  score?: number;
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({ level, size = 'md', score }) => {
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1 font-semibold',
    lg: 'text-sm px-3.5 py-1.5 font-bold tracking-wide'
  };

  const config = {
    CRITICAL: {
      bg: 'bg-rose-950/70 border-rose-500/60 text-rose-300 shadow-[0_0_12px_rgba(244,63,94,0.35)]',
      dot: 'bg-rose-500 animate-ping'
    },
    HIGH: {
      bg: 'bg-orange-950/70 border-orange-500/60 text-orange-300 shadow-[0_0_10px_rgba(249,115,22,0.25)]',
      dot: 'bg-orange-500'
    },
    MEDIUM: {
      bg: 'bg-amber-950/70 border-amber-500/60 text-amber-300',
      dot: 'bg-amber-500'
    },
    LOW: {
      bg: 'bg-emerald-950/70 border-emerald-500/60 text-emerald-300',
      dot: 'bg-emerald-500'
    }
  };

  const item = config[level] || config.LOW;

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border ${item.bg} ${sizeClasses[size]}`}>
      <span className="relative flex h-2 w-2">
        {level === 'CRITICAL' && (
          <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 ${item.dot}`}></span>
        )}
        <span className={`relative inline-flex rounded-full h-2 w-2 ${item.dot}`}></span>
      </span>
      <span>{level}</span>
      {score !== undefined && (
        <span className="opacity-80 font-mono text-[11px] ml-0.5">({score.toFixed(1)})</span>
      )}
    </span>
  );
};
