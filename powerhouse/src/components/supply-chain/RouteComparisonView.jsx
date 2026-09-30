import React, { useState } from 'react';
import {
  Navigation,
  ArrowRight,
  Clock,
  DollarSign,
  AlertTriangle,
  CheckCircle2,
  Cpu,
  ShieldCheck,
  Ship,
} from 'lucide-react';
import Button from '../ui/Button';

export default function RouteComparisonView({ routeData, onApproveReroute }) {
  const [selectedRouteKey, setSelectedRouteKey] = useState('TSMC_DALLAS');

  const comparison = routeData || {
    disrupted_segment: 'Port of Kaohsiung',
    original_route: {
      path: ['Supplier (TSMC Hsinchu)', 'Port of Kaohsiung', 'Port of Long Beach', 'DC South (Dallas Hub)'],
      distance_km: 11450.0,
      eta_days: 4.2,
      cost_usd: 62000.0,
      co2_kg: 8400.0,
    },
    optimized_reroute: {
      path: ['Supplier (TSMC Hsinchu)', 'Port of Busan', 'Port of Oakland', 'DC South (Dallas Hub)'],
      distance_km: 12280.0,
      eta_days: 4.8,
      cost_usd: 68500.0,
      co2_kg: 8920.0,
    },
    comparison: {
      delay_hours: 14.4,
      cost_increase_usd: 6500.0,
      cost_increase_pct: 10.5,
      distance_delta_km: 830.0,
      co2_delta_pct: 6.2,
    },
    recommendation: 'Reroute shipment via Port of Busan and Oakland to circumvent 8-day Kaohsiung port closure.',
    human_approval_required: true,
  };

  const orig = comparison.original_route;
  const opt = comparison.optimized_reroute;
  const delta = comparison.comparison;

  return (
    <div className="bg-[#111827] rounded-2xl border border-[#1E293B] p-5 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold text-white">Logistics Rerouting & Corridor Optimization</h3>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-blue-950/70 text-blue-300 border border-blue-800 font-mono">
              Google OR-Tools Engine
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Mathematical shortest path & capacity constrained corridor rerouting
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-950 text-amber-300 border border-amber-800">
            HUMAN APPROVAL REQUIRED
          </span>
        </div>
      </div>

      {/* Visual Route Pipeline Diagrams */}
      <div className="space-y-4">
        {/* Original Disrupted Route */}
        <div className="p-4 rounded-xl bg-[#0B1120] border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-slate-500" />
              Primary Route (Disrupted)
            </span>
            <span className="text-[11px] font-mono text-rose-400 font-bold flex items-center gap-1">
              <AlertTriangle className="w-3.5 h-3.5" />
              Blocked Segment: {comparison.disrupted_segment}
            </span>
          </div>

          <div className="flex items-center gap-2 flex-wrap pt-2">
            {orig.path.map((step, idx) => {
              const isBlocked = step.toLowerCase().includes('kaohsiung');

              return (
                <React.Fragment key={idx}>
                  <div
                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold border flex items-center gap-1.5 ${
                      isBlocked
                        ? 'bg-rose-950/90 border-rose-700 text-rose-300 line-through'
                        : 'bg-slate-900 border-slate-800 text-slate-300'
                    }`}
                  >
                    <span>{step}</span>
                    {isBlocked && <span className="text-[9px] font-black text-rose-400">BLOCKED</span>}
                  </div>
                  {idx < orig.path.length - 1 && (
                    <ArrowRight className={`w-3.5 h-3.5 shrink-0 ${isBlocked ? 'text-rose-500' : 'text-slate-600'}`} />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* AI Optimized Reroute */}
        <div className="p-4 rounded-xl bg-[#0B1120] border border-cyan-900/60 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-cyan-400" />
              OR-Tools Recommended Reroute (Busan Bypass)
            </span>
            <span className="text-[11px] font-mono text-emerald-400 font-bold flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Continuous Flow Maintained
            </span>
          </div>

          <div className="flex items-center gap-2 flex-wrap pt-2">
            {opt.path.map((step, idx) => {
              const isBypass = step.toLowerCase().includes('busan') || step.toLowerCase().includes('oakland');

              return (
                <React.Fragment key={idx}>
                  <div
                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold border flex items-center gap-1.5 ${
                      isBypass
                        ? 'bg-cyan-950/90 border-cyan-700 text-cyan-300 shadow-sm shadow-cyan-900/40'
                        : 'bg-slate-900 border-slate-800 text-slate-300'
                    }`}
                  >
                    <span>{step}</span>
                    {isBypass && <span className="text-[9px] font-black text-cyan-400">AI BYPASS</span>}
                  </div>
                  {idx < opt.path.length - 1 && (
                    <ArrowRight className="w-3.5 h-3.5 shrink-0 text-cyan-600" />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>
      </div>

      {/* Quantitative Trade-Off Comparison Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <div className="p-3 rounded-xl bg-[#0B1120] border border-slate-800">
          <span className="text-[10px] text-slate-400 uppercase block">Transit ETA Delta</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-base font-black text-white">{orig.eta_days}d</span>
            <span className="text-slate-500">→</span>
            <span className="text-base font-black text-amber-400">{opt.eta_days}d</span>
          </div>
          <span className="text-[10px] text-amber-400 mt-1 block">+{delta.delay_hours} hrs total delay</span>
        </div>

        <div className="p-3 rounded-xl bg-[#0B1120] border border-slate-800">
          <span className="text-[10px] text-slate-400 uppercase block">Freight Cost Delta</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-base font-black text-white">${(orig.cost_usd / 1000).toFixed(0)}k</span>
            <span className="text-slate-500">→</span>
            <span className="text-base font-black text-amber-400">${(opt.cost_usd / 1000).toFixed(1)}k</span>
          </div>
          <span className="text-[10px] text-amber-400 mt-1 block">+${delta.cost_increase_usd.toLocaleString()} (+{delta.cost_increase_pct}%)</span>
        </div>

        <div className="p-3 rounded-xl bg-[#0B1120] border border-slate-800">
          <span className="text-[10px] text-slate-400 uppercase block">Distance Delta</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-base font-black text-white">{orig.distance_km.toLocaleString()}</span>
            <span className="text-slate-500">→</span>
            <span className="text-base font-black text-slate-200">{opt.distance_km.toLocaleString()}</span>
          </div>
          <span className="text-[10px] text-slate-400 mt-1 block">+{delta.distance_delta_km} km maritime</span>
        </div>

        <div className="p-3 rounded-xl bg-[#0B1120] border border-slate-800">
          <span className="text-[10px] text-slate-400 uppercase block">Avoided Line Shutdown</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-base font-black text-emerald-400">8 to 11 days</span>
          </div>
          <span className="text-[10px] text-emerald-400 mt-1 block">Saves est. $420,000</span>
        </div>
      </div>

      {/* Action Footer */}
      <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div className="text-slate-300">
          <span className="font-bold text-white">OR-Tools Recommendation: </span>
          {comparison.recommendation}
        </div>
        <Button
          variant="primary"
          size="sm"
          onClick={() => onApproveReroute && onApproveReroute(comparison)}
          className="bg-blue-600 hover:bg-blue-500 text-white text-xs shrink-0"
        >
          Approve Reroute Authorization
        </Button>
      </div>
    </div>
  );
}
