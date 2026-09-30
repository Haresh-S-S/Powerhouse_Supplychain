import React, { useState } from 'react';
import {
  TrendingDown,
  ShieldCheck,
  Clock,
  AlertCircle,
  Zap,
} from 'lucide-react';

export default function DisruptionImpactChart({ impactData, selectedDisruption }) {
  const [hoveredDay, setHoveredDay] = useState(null);

  const timeline = impactData?.timeline || [];
  const metrics = impactData?.metrics || {
    supply_impact_pct: 28.0,
    expected_delay_days: 9.0,
    recovery_time_days: 4.0,
    residual_risk_pct: 11.0,
  };

  const maxVal = Math.max(...timeline.map((d) => Math.max(d.baseline_demand, d.ai_recovered_supply, d.disrupted_supply)), 1500);
  const minVal = 0;

  const width = 760;
  const height = 240;
  const padding = { top: 20, right: 30, bottom: 35, left: 50 };

  const graphWidth = width - padding.left - padding.right;
  const graphHeight = height - padding.top - padding.bottom;

  const getX = (index) => padding.left + (index / Math.max(timeline.length - 1, 1)) * graphWidth;
  const getY = (val) => padding.top + graphHeight - ((val - minVal) / (maxVal - minVal)) * graphHeight;

  // Build SVG path strings
  const baselinePath = timeline
    .map((d, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(d.baseline_demand)}`)
    .join(' ');

  const disruptedPath = timeline
    .map((d, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(d.disrupted_supply)}`)
    .join(' ');

  const aiPath = timeline
    .map((d, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(d.ai_recovered_supply)}`)
    .join(' ');

  // Shaded area between Baseline and AI Recovered
  const areaAi = `${aiPath} L ${getX(timeline.length - 1)} ${padding.top + graphHeight} L ${getX(0)} ${padding.top + graphHeight} Z`;

  // Active hover point
  const activePoint = hoveredDay !== null ? timeline[hoveredDay] : timeline[10] || timeline[0];

  return (
    <div className="bg-[#111827] rounded-2xl border border-[#1E293B] p-5 space-y-4">
      {/* Title & Key Quantitative Stat Badges */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold text-white">Disruption Impact & Recovery Curve</h3>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-rose-950/70 text-rose-300 border border-rose-800 font-mono">
              SupplyMind Engine
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Baseline Demand vs Disrupted Supply vs AI-Recovered Response (30-Day Simulation)
          </p>
        </div>

        {/* 4 Quantitative Impact Badges */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl px-2.5 py-1.5 flex flex-col">
            <span className="text-[9px] font-bold text-slate-400 uppercase">Supply Impact</span>
            <span className="text-xs font-black text-rose-400">-{metrics.supply_impact_pct}%</span>
          </div>
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl px-2.5 py-1.5 flex flex-col">
            <span className="text-[9px] font-bold text-slate-400 uppercase">Expected Delay</span>
            <span className="text-xs font-black text-amber-400">+{metrics.expected_delay_days} days</span>
          </div>
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl px-2.5 py-1.5 flex flex-col">
            <span className="text-[9px] font-bold text-slate-400 uppercase">Recovery Time</span>
            <span className="text-xs font-black text-emerald-400">{metrics.recovery_time_days} days</span>
          </div>
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl px-2.5 py-1.5 flex flex-col">
            <span className="text-[9px] font-bold text-slate-400 uppercase">Residual Risk</span>
            <span className="text-xs font-black text-cyan-400">{metrics.residual_risk_pct}%</span>
          </div>
        </div>
      </div>

      {/* SVG Chart Area */}
      <div className="relative bg-[#0B1120] rounded-xl border border-slate-800/80 p-3 overflow-x-auto scrollbar-thin">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-auto min-w-[620px]"
          onMouseLeave={() => setHoveredDay(null)}
        >
          <defs>
            <linearGradient id="aiAreaGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#0284C7" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#0284C7" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Horizontal Grid lines */}
          {[0.25, 0.5, 0.75, 1.0].map((frac) => {
            const yVal = padding.top + graphHeight * (1 - frac);
            const labelVal = Math.round(minVal + frac * (maxVal - minVal));
            return (
              <g key={frac}>
                <line x1={padding.left} y1={yVal} x2={width - padding.right} y2={yVal} stroke="#1E293B" strokeWidth="0.8" strokeDasharray="3 3" />
                <text x={padding.left - 8} y={yVal + 3} textAnchor="end" fill="#64748B" fontSize="9">
                  {labelVal}
                </text>
              </g>
            );
          })}

          {/* AI Recovered Area Fill */}
          <path d={areaAi} fill="url(#aiAreaGrad)" />

          {/* Baseline Demand Line (Gray dashed) */}
          <path d={baselinePath} fill="none" stroke="#64748B" strokeWidth="1.8" strokeDasharray="4 4" />

          {/* Disrupted Supply Line (Red solid) */}
          <path d={disruptedPath} fill="none" stroke="#F43F5E" strokeWidth="2.2" opacity="0.9" />

          {/* AI-Recovered Supply Line (Cyan solid) */}
          <path d={aiPath} fill="none" stroke="#38BDF8" strokeWidth="2.5" />

          {/* Timeline points / hover triggers */}
          {timeline.map((d, i) => (
            <g key={i} onMouseEnter={() => setHoveredDay(i)}>
              <rect
                x={getX(i) - 6}
                y={padding.top}
                width="12"
                height={graphHeight}
                fill="transparent"
                className="cursor-crosshair"
              />
            </g>
          ))}

          {/* Active Hover Marker Line */}
          {hoveredDay !== null && (
            <line
              x1={getX(hoveredDay)}
              y1={padding.top}
              x2={getX(hoveredDay)}
              y2={padding.top + graphHeight}
              stroke="#94A3B8"
              strokeWidth="1.2"
              strokeDasharray="2 2"
            />
          )}

          {/* Day X-Axis Labels */}
          {timeline.filter((_, i) => i % 5 === 0 || i === timeline.length - 1).map((d) => {
            const idx = timeline.indexOf(d);
            return (
              <text key={idx} x={getX(idx)} y={height - 12} textAnchor="middle" fill="#64748B" fontSize="9" fontWeight="600">
                Day {d.day}
              </text>
            );
          })}
        </svg>

        {/* Hover Inspector Tooltip */}
        {activePoint && (
          <div className="absolute top-4 right-4 bg-slate-950/90 backdrop-blur-md border border-slate-700 rounded-xl p-2.5 text-[11px] shadow-xl space-y-1">
            <span className="font-bold text-white block border-b border-slate-800 pb-1">
              Timeline: Day {activePoint.day} Telemetry
            </span>
            <div className="flex items-center justify-between gap-4 text-slate-300">
              <span className="flex items-center gap-1.5 text-slate-400">
                <span className="w-2 h-0.5 bg-slate-400 inline-block" /> Baseline:
              </span>
              <span className="font-mono font-bold">{activePoint.baseline_demand} u</span>
            </div>
            <div className="flex items-center justify-between gap-4 text-rose-300">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-0.5 bg-rose-400 inline-block" /> Disrupted:
              </span>
              <span className="font-mono font-bold">{activePoint.disrupted_supply} u</span>
            </div>
            <div className="flex items-center justify-between gap-4 text-cyan-300">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-0.5 bg-cyan-400 inline-block" /> AI-Recovered:
              </span>
              <span className="font-mono font-bold">{activePoint.ai_recovered_supply} u</span>
            </div>
          </div>
        )}
      </div>

      {/* Legend & Context Note */}
      <div className="flex flex-wrap items-center justify-between text-xs text-slate-400 pt-1 border-t border-slate-800/80 gap-3">
        <div className="flex items-center gap-4 flex-wrap">
          <span className="flex items-center gap-1.5 text-slate-400">
            <span className="w-3 h-0.5 bg-slate-400 inline-block" /> Baseline Demand
          </span>
          <span className="flex items-center gap-1.5 text-rose-400">
            <span className="w-3 h-0.5 bg-rose-500 inline-block" /> Disrupted Supply (Unmitigated)
          </span>
          <span className="flex items-center gap-1.5 text-cyan-400">
            <span className="w-3 h-0.5 bg-cyan-400 inline-block" /> AI-Recovered Supply (OR-Tools + Rebalance)
          </span>
        </div>
        <div className="text-[11px] text-emerald-400 font-semibold flex items-center gap-1">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>AI shortens recovery from 16 to 4 days</span>
        </div>
      </div>
    </div>
  );
}
