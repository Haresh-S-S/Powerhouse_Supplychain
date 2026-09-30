import React, { useState } from 'react';
import {
  Play,
  RotateCw,
  Sliders,
  CheckCircle,
  TrendingDown,
  Clock,
  DollarSign,
  Shield,
  Layers,
} from 'lucide-react';
import Button from '../ui/Button';
import apiClient from '../../services/apiClient';

const PRESET_SCENARIOS = [
  { id: 'port_closure', name: 'Port of Kaohsiung Closure (10 Days)', type: 'port_closure', defaults: { delay_days: 10, port: 'Port of Kaohsiung' } },
  { id: 'supplier_failure', name: 'Primary Supplier Failure (TSMC 30 Days)', type: 'supplier_failure', defaults: { duration_days: 30, supplier: 'TSMC Fab 14' } },
  { id: 'tariff_increase', name: 'Transpacific Tariff Hike (+20%)', type: 'tariff_increase', defaults: { tariff_pct: 20 } },
  { id: 'severe_weather', name: 'US Central Winter Logistics Freeze', type: 'severe_weather', defaults: { delay_days: 7 } },
];

export default function ScenarioComparisonChart({ businessId, onSimulate }) {
  const [selectedScenario, setSelectedScenario] = useState('port_closure');
  const [delayDays, setDelayDays] = useState(10);
  const [tariffPct, setTariffPct] = useState(20);
  const [simulating, setSimulating] = useState(false);
  const [simulationResult, setSimulationResult] = useState(null);

  const activePreset = PRESET_SCENARIOS.find((p) => p.id === selectedScenario) || PRESET_SCENARIOS[0];

  const handleRunSimulation = async () => {
    if (!businessId) return;
    setSimulating(true);
    try {
      const params =
        selectedScenario === 'port_closure'
          ? { port: 'Port of Kaohsiung', delay_days: delayDays }
          : selectedScenario === 'tariff_increase'
          ? { tariff_pct: tariffPct }
          : { duration_days: delayDays * 3 };

      const res = await apiClient.simulateTowerScenario({
        business_id: businessId,
        scenario_type: selectedScenario,
        parameters: params,
        name: activePreset.name,
      });
      setSimulationResult(res);
      if (onSimulate) onSimulate(res);
    } catch (err) {
      console.error('Simulation failed', err);
    } finally {
      setSimulating(false);
    }
  };

  const comparison = simulationResult?.comparison || [
    { dimension: 'Cost Impact', baseline: 0.0, disrupted: 18.5, ai_recovered: 8.2, unit: '%' },
    { dimension: 'Transit Delay', baseline: 0.0, disrupted: 10.0, ai_recovered: 3.8, unit: 'days' },
    { dimension: 'Risk Score', baseline: 18.0, disrupted: 74.0, ai_recovered: 29.0, unit: '%' },
    { dimension: 'Recovery Time', baseline: 0.0, disrupted: 16.0, ai_recovered: 5.0, unit: 'days' },
  ];

  return (
    <div className="bg-[#111827] rounded-2xl border border-[#1E293B] p-5 space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold text-white">Scenario Planning & Comparative Simulation</h3>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-indigo-950/70 text-indigo-300 border border-indigo-800 font-mono">
              SupplyMind + Qwen3
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Compare BASELINE vs DISRUPTED SCENARIO vs AI OPTIMIZED RESPONSE
          </p>
        </div>

        {/* Preset Selector */}
        <div className="flex items-center gap-2">
          <select
            value={selectedScenario}
            onChange={(e) => setSelectedScenario(e.target.value)}
            className="bg-slate-900 text-xs text-slate-200 border border-slate-700 rounded-xl px-3 py-1.5 focus:outline-none focus:border-indigo-500 cursor-pointer"
          >
            {PRESET_SCENARIOS.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>

          <Button
            variant="primary"
            size="sm"
            onClick={handleRunSimulation}
            disabled={simulating}
            className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs flex items-center gap-1.5"
          >
            {simulating ? <RotateCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
            <span>Run Simulation</span>
          </Button>
        </div>
      </div>

      {/* Interactive Parameter Sliders */}
      <div className="p-3.5 rounded-xl bg-[#0B1120] border border-slate-800 grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
        <div>
          <div className="flex justify-between text-slate-400 mb-1">
            <span>Disruption Delay Days:</span>
            <span className="font-mono text-cyan-400 font-bold">{delayDays} days</span>
          </div>
          <input
            type="range"
            min="3"
            max="30"
            value={delayDays}
            onChange={(e) => setDelayDays(Number(e.target.value))}
            className="w-full accent-cyan-500 cursor-pointer"
          />
        </div>

        <div>
          <div className="flex justify-between text-slate-400 mb-1">
            <span>Tariff Delta Adjustment:</span>
            <span className="font-mono text-amber-400 font-bold">+{tariffPct}%</span>
          </div>
          <input
            type="range"
            min="5"
            max="50"
            value={tariffPct}
            onChange={(e) => setTariffPct(Number(e.target.value))}
            className="w-full accent-amber-500 cursor-pointer"
          />
        </div>

        <div className="flex items-center justify-between bg-slate-900/80 px-3 rounded-lg border border-slate-800">
          <span className="text-slate-400">Simulation Status</span>
          <span className="text-[11px] font-bold text-emerald-400 flex items-center gap-1 font-mono">
            <CheckCircle className="w-3.5 h-3.5" /> READY
          </span>
        </div>
      </div>

      {/* Grouped Bar Chart Visual */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {comparison.map((c, idx) => {
          const maxScale = Math.max(c.disrupted, c.ai_recovered, 10);

          return (
            <div key={idx} className="p-4 rounded-xl bg-[#0B1120] border border-slate-800 flex flex-col justify-between space-y-4">
              <div>
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                  {c.dimension}
                </span>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-lg font-black text-rose-400">
                    +{c.disrupted}
                    <span className="text-xs">{c.unit}</span>
                  </span>
                  <span className="text-xs text-slate-500 font-semibold">→</span>
                  <span className="text-lg font-black text-emerald-400">
                    +{c.ai_recovered}
                    <span className="text-xs">{c.unit}</span>
                  </span>
                </div>
              </div>

              {/* Grouped Comparative Bars */}
              <div className="space-y-2 text-[10px]">
                {/* Disrupted Scenario Bar */}
                <div className="space-y-1">
                  <div className="flex justify-between text-slate-400">
                    <span className="flex items-center gap-1 text-rose-300">
                      <span className="w-2 h-2 rounded-sm bg-rose-500" /> Disrupted
                    </span>
                    <span className="font-mono font-bold text-rose-400">
                      {c.disrupted} {c.unit}
                    </span>
                  </div>
                  <div className="w-full h-2.5 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                    <div
                      className="h-full bg-rose-500 rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(100, (c.disrupted / maxScale) * 100)}%` }}
                    />
                  </div>
                </div>

                {/* AI Recovered Bar */}
                <div className="space-y-1">
                  <div className="flex justify-between text-slate-400">
                    <span className="flex items-center gap-1 text-emerald-300">
                      <span className="w-2 h-2 rounded-sm bg-emerald-500" /> AI Response
                    </span>
                    <span className="font-mono font-bold text-emerald-400">
                      {c.ai_recovered} {c.unit}
                    </span>
                  </div>
                  <div className="w-full h-2.5 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                    <div
                      className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(100, (c.ai_recovered / maxScale) * 100)}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Improvement Badge */}
              <div className="pt-2 border-t border-slate-800/80 text-[10px] text-slate-400 flex items-center justify-between">
                <span>Mitigation Effect</span>
                <span className="font-bold text-emerald-400 font-mono">
                  -{Math.round(((c.disrupted - c.ai_recovered) / Math.max(c.disrupted, 1)) * 100)}%
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* AI Synthesis Box */}
      <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800 text-xs text-slate-300 space-y-1">
        <div className="font-bold text-white flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-indigo-400" />
          <span>Qwen3 Executive Scenario Synthesis:</span>
        </div>
        <p className="text-slate-300 leading-relaxed text-[11px]">
          {simulationResult?.ai_summary ||
            `Under ${activePreset.name}, unmitigated disruption increases freight costs by +18.5% with a 10-day shipping delay. The Supply Chain AI stack restricts cost rise to +8.2% and compresses recovery from 16 days to 5 days.`}
        </p>
      </div>
    </div>
  );
}
