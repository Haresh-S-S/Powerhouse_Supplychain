import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  Calendar,
  Layers,
  Sparkles,
  Filter,
  CheckCircle2,
} from 'lucide-react';
import apiClient from '../../services/apiClient';

const SKUS = [
  { id: 'SKU-DRAM-001', name: 'DRAM-16GB-DDR5', cat: 'Memory' },
  { id: 'SKU-MCU-002', name: 'Automotive 32-Bit MCU', cat: 'Semiconductors' },
  { id: 'SKU-MOSFET-003', name: 'SiC 1200V MOSFET', cat: 'Power' },
  { id: 'SKU-RADAR-010', name: '77GHz mmWave Radar', cat: 'Sensors' },
];

const WAREHOUSES = [
  { id: 'ALL', name: 'Consolidated Network' },
  { id: 'DC-SOUTH', name: 'DC South (Dallas Regional)' },
  { id: 'DC-NORTH', name: 'DC North (Hamburg Hub)' },
  { id: 'DC-WEST', name: 'DC West (Tokyo Hub)' },
];

export default function DemandForecastChart({ businessId, initialSku = 'SKU-DRAM-001' }) {
  const [selectedSku, setSelectedSku] = useState(initialSku);
  const [selectedWarehouse, setSelectedWarehouse] = useState('DC-SOUTH');
  const [horizon, setHorizon] = useState(30);
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;
    async function loadForecast() {
      if (!businessId) return;
      setLoading(true);
      try {
        const res = await apiClient.getTowerForecast({
          business_id: businessId,
          sku: selectedSku,
          warehouse_id: selectedWarehouse === 'ALL' ? null : selectedWarehouse,
          horizon_days: horizon,
        });
        if (isMounted) setForecastData(res);
      } catch (err) {
        console.error('Forecast load error', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadForecast();
    return () => {
      isMounted = false;
    };
  }, [businessId, selectedSku, selectedWarehouse, horizon]);

  const history = forecastData?.historical_series || [120, 128, 135, 130, 142, 138, 145, 150, 142, 148, 155, 160, 152, 158, 164];
  const p50 = forecastData?.forecast_p50 || [166, 170, 172, 175, 180, 182, 185, 188, 190, 192, 195, 198, 202, 205];
  const p10 = forecastData?.forecast_p10 || p50.map((v) => Math.round(v * 0.88));
  const p90 = forecastData?.forecast_p90 || p50.map((v) => Math.round(v * 1.14));

  const totalPoints = history.length + p50.length;
  const allValues = [...history, ...p90, ...p10];
  const maxVal = Math.max(...allValues, 220);
  const minVal = Math.min(...allValues, 100);

  const width = 760;
  const height = 240;
  const padding = { top: 20, right: 30, bottom: 35, left: 50 };

  const graphWidth = width - padding.left - padding.right;
  const graphHeight = height - padding.top - padding.bottom;

  const getX = (idx) => padding.left + (idx / Math.max(totalPoints - 1, 1)) * graphWidth;
  const getY = (val) => padding.top + graphHeight - ((val - minVal) / (maxVal - minVal)) * graphHeight;

  // Historical path
  const historyPath = history
    .map((d, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(d)}`)
    .join(' ');

  // Connect history to forecast
  const lastHistIdx = history.length - 1;
  const lastHistX = getX(lastHistIdx);
  const lastHistY = getY(history[lastHistIdx]);

  // P50 line path
  const p50Path = `M ${lastHistX} ${lastHistY} ` + p50.map((d, i) => `L ${getX(history.length + i)} ${getY(d)}`).join(' ');

  // P10 & P90 confidence area
  const confidenceArea =
    `M ${lastHistX} ${lastHistY} ` +
    p90.map((d, i) => `L ${getX(history.length + i)} ${getY(d)}`).join(' ') +
    p10
      .slice()
      .reverse()
      .map((d, i) => `L ${getX(history.length + p10.length - 1 - i)} ${getY(d)}`)
      .join(' ') +
    ' Z';

  const pctChange = forecastData?.percentage_change ?? 14.6;

  return (
    <div className="bg-[#111827] rounded-2xl border border-[#1E293B] p-5 space-y-4">
      {/* Top Controls Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold text-white">Demand Forecasting & Confidence Range</h3>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-cyan-950/70 text-cyan-300 border border-cyan-800 font-mono">
              Inventory Fusion Engine
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Fused MovingAverage + Seasonal Naive multi-quantile projection
          </p>
        </div>

        {/* Forecast KPI Pill */}
        <div className="flex items-center gap-3">
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl px-3 py-1.5 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-emerald-400" />
            <div>
              <span className="text-[9px] uppercase font-bold text-slate-400 block">Next 30 Days Forecast</span>
              <span className="text-xs font-black text-emerald-400">+{pctChange}% growth</span>
            </div>
          </div>

          {/* Sku Dropdown */}
          <select
            value={selectedSku}
            onChange={(e) => setSelectedSku(e.target.value)}
            className="bg-slate-900 text-xs text-slate-200 border border-slate-700 rounded-xl px-2.5 py-1.5 focus:outline-none focus:border-cyan-500 cursor-pointer"
          >
            {SKUS.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>

          {/* Warehouse Dropdown */}
          <select
            value={selectedWarehouse}
            onChange={(e) => setSelectedWarehouse(e.target.value)}
            className="bg-slate-900 text-xs text-slate-200 border border-slate-700 rounded-xl px-2.5 py-1.5 focus:outline-none focus:border-cyan-500 cursor-pointer"
          >
            {WAREHOUSES.map((w) => (
              <option key={w.id} value={w.id}>
                {w.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* SVG Forecast Graph */}
      <div className="relative bg-[#0B1120] rounded-xl border border-slate-800/80 p-3 overflow-x-auto scrollbar-thin">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto min-w-[620px]">
          <defs>
            <linearGradient id="confidenceGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#06B6D4" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#06B6D4" stopOpacity="0.05" />
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

          {/* Confidence Area Band (p10 to p90) */}
          <path d={confidenceArea} fill="url(#confidenceGrad)" />

          {/* Historical Demand Line (Solid Indigo) */}
          <path d={historyPath} fill="none" stroke="#818CF8" strokeWidth="2.4" />

          {/* Forecast P50 Line (Dashed Cyan) */}
          <path d={p50Path} fill="none" stroke="#22D3EE" strokeWidth="2.4" strokeDasharray="4 3" />

          {/* Demarcation line: Today / Forecast Start */}
          <line
            x1={lastHistX}
            y1={padding.top}
            x2={lastHistX}
            y2={padding.top + graphHeight}
            stroke="#94A3B8"
            strokeWidth="1.2"
            strokeDasharray="3 3"
          />
          <text x={lastHistX} y={padding.top + 10} textAnchor="middle" fill="#94A3B8" fontSize="8" fontWeight="bold">
            TODAY
          </text>

          {/* Historical Data Points */}
          {history.map((d, i) => (
            <circle key={i} cx={getX(i)} cy={getY(d)} r="2.5" fill="#818CF8" />
          ))}

          {/* X Axis Labels */}
          <text x={getX(0)} y={height - 12} textAnchor="start" fill="#64748B" fontSize="9">
            -30 Days
          </text>
          <text x={lastHistX} y={height - 12} textAnchor="middle" fill="#94A3B8" fontSize="9">
            Day 0
          </text>
          <text x={getX(totalPoints - 1)} y={height - 12} textAnchor="end" fill="#22D3EE" fontSize="9">
            +30 Days Horizon
          </text>
        </svg>
      </div>

      {/* Legend & Details */}
      <div className="flex flex-wrap items-center justify-between text-xs text-slate-400 pt-1 border-t border-slate-800/80 gap-3">
        <div className="flex items-center gap-4 flex-wrap">
          <span className="flex items-center gap-1.5 text-indigo-300">
            <span className="w-3 h-0.5 bg-indigo-400 inline-block" /> Historical Demand (Actual)
          </span>
          <span className="flex items-center gap-1.5 text-cyan-300">
            <span className="w-3 h-0.5 bg-cyan-400 border-t border-dashed inline-block" /> Forecast Demand (P50 Point)
          </span>
          <span className="flex items-center gap-1.5 text-cyan-400">
            <span className="w-3 h-2 bg-cyan-500/20 border border-cyan-400/40 inline-block" /> Confidence Band (P10 - P90)
          </span>
        </div>
        <div className="text-[11px] text-cyan-300 font-mono">
          Predicted 30d Total: {forecastData?.predicted_total_30d?.toLocaleString() || '4,850'} units
        </div>
      </div>
    </div>
  );
}
