import React from 'react';
import { PriorityLevel } from '../types';

interface ScoreGaugeProps {
  score: number;
  mlScore?: number;
  ruleScore?: number;
  level: PriorityLevel;
  size?: 'sm' | 'md' | 'lg';
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({
  score,
  mlScore,
  ruleScore,
  level,
  size = 'md'
}) => {
  const levelColors: Record<PriorityLevel, string> = {
    CRITICAL: '#f43f5e',
    HIGH: '#f97316',
    MEDIUM: '#f59e0b',
    LOW: '#10b981'
  };

  const color = levelColors[level] || '#06b6d4';
  const radius = size === 'sm' ? 24 : size === 'md' ? 36 : 48;
  const stroke = size === 'sm' ? 4 : size === 'md' ? 6 : 8;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const width = radius * 2;
  const height = radius * 2;

  return (
    <div className="flex items-center gap-3">
      <div className="relative inline-flex items-center justify-center">
        <svg height={height} width={width} className="transform -rotate-90">
          <circle
            stroke="#1e293b"
            fill="transparent"
            strokeWidth={stroke}
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
          <circle
            stroke={color}
            fill="transparent"
            strokeWidth={stroke}
            strokeDasharray={circumference + ' ' + circumference}
            style={{ strokeDashoffset, transition: 'stroke-dashoffset 0.6s ease' }}
            strokeLinecap="round"
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
        </svg>
        <div className="absolute text-center">
          <span className={`font-mono font-bold ${size === 'sm' ? 'text-xs' : size === 'md' ? 'text-base' : 'text-xl'}`} style={{ color }}>
            {score.toFixed(1)}
          </span>
        </div>
      </div>

      {(mlScore !== undefined || ruleScore !== undefined) && size !== 'sm' && (
        <div className="flex flex-col gap-1.5 min-w-[130px] text-xs font-mono">
          {mlScore !== undefined && (
            <div>
              <div className="flex justify-between text-[10px] text-slate-400 mb-0.5">
                <span className="flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 inline-block"></span>
                  ML (65%)
                </span>
                <span className="font-bold text-cyan-300">{mlScore.toFixed(1)}</span>
              </div>
              <div className="w-full bg-slate-800/80 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-cyan-400 h-full rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, mlScore)}%` }}
                />
              </div>
            </div>
          )}

          {ruleScore !== undefined && (
            <div>
              <div className="flex justify-between text-[10px] text-slate-400 mb-0.5">
                <span className="flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-purple-400 inline-block"></span>
                  Rule (35%)
                </span>
                <span className="font-bold text-purple-300">{ruleScore.toFixed(1)}</span>
              </div>
              <div className="w-full bg-slate-800/80 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-purple-400 h-full rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, ruleScore)}%` }}
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
