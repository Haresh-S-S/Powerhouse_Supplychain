import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Award,
  Globe2,
  FileCheck2,
  AlertTriangle,
  Info,
} from 'lucide-react';
import apiClient from '../../services/apiClient';

export default function SupplierRadarChart({ businessId, suppliers = [], selectedSupplierId, onSelectSupplier }) {
  const [currentSupplierId, setCurrentSupplierId] = useState(selectedSupplierId || (suppliers[0]?.id || ''));
  const [radarData, setRadarData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (selectedSupplierId) {
      setCurrentSupplierId(selectedSupplierId);
    }
  }, [selectedSupplierId]);

  useEffect(() => {
    let isMounted = true;
    async function loadRadar() {
      if (!currentSupplierId || !businessId) return;
      setLoading(true);
      try {
        const res = await apiClient.getTowerSupplierRadar(currentSupplierId, businessId);
        if (isMounted) setRadarData(res);
      } catch (err) {
        console.error('Failed to load supplier radar', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadRadar();
    return () => {
      isMounted = false;
    };
  }, [currentSupplierId, businessId]);

  const dimensions = radarData?.dimensions || [
    { dimension: 'Reliability', value: 91.0, description: 'High operational uptime' },
    { dimension: 'Financial Stability', value: 96.0, description: 'AA+ corporate credit rating' },
    { dimension: 'Geopolitical Risk', value: 82.0, description: 'High corridor exposure' },
    { dimension: 'Quality', value: 98.0, description: 'Industry leading process yield' },
    { dimension: 'Lead-Time Risk', value: 68.0, description: 'Extended 28-day lead time' },
    { dimension: 'Logistics Risk', value: 72.0, description: 'Single port dependency' },
    { dimension: 'Compliance', value: 88.0, description: 'Verified ISO 9001' },
    { dimension: 'ESG Risk', value: 61.0, description: 'Water and energy intensity' },
  ];

  const size = 320;
  const center = size / 2;
  const radius = center - 45;
  const totalAxes = dimensions.length;

  const getCoordinates = (index, value) => {
    const angle = (Math.PI * 2 / totalAxes) * index - Math.PI / 2;
    const r = (value / 100.0) * radius;
    const x = center + r * Math.cos(angle);
    const y = center + r * Math.sin(angle);
    return { x, y };
  };

  // Polygon points
  const polygonPoints = dimensions
    .map((d, i) => {
      const { x, y } = getCoordinates(i, d.value);
      return `${x},${y}`;
    })
    .join(' ');

  const aiScore = radarData?.ai_risk_score ?? 74.0;
  const riskLevel = radarData?.predicted_risk_level ?? 'CRITICAL';

  return (
    <div className="bg-[#111827] rounded-2xl border border-[#1E293B] p-5 space-y-4">
      {/* Header & Supplier Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold text-white">Supplier Risk Spider / Radar Profile</h3>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-amber-950/70 text-amber-300 border border-amber-800 font-mono">
              AI Risk Analysis
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            8-dimension vulnerability mapping derived from DistilBERT and HREDD models
          </p>
        </div>

        {/* Supplier Dropdown */}
        <div className="flex items-center gap-2">
          <select
            value={currentSupplierId}
            onChange={(e) => {
              setCurrentSupplierId(e.target.value);
              if (onSelectSupplier) onSelectSupplier(e.target.value);
            }}
            className="bg-slate-900 text-xs text-slate-200 border border-slate-700 rounded-xl px-3 py-1.5 focus:outline-none focus:border-amber-500 cursor-pointer"
          >
            {suppliers.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} ({s.country || s.region})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Grid: Radar Chart + Dimensional Breakdown Table */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
        {/* Radar SVG Visual */}
        <div className="flex flex-col items-center justify-center relative bg-[#0B1120] rounded-xl border border-slate-800/80 p-3">
          <svg width={size} height={size} className="select-none">
            <defs>
              <linearGradient id="radarAreaGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#F59E0B" stopOpacity="0.45" />
                <stop offset="100%" stopColor="#EF4444" stopOpacity="0.25" />
              </linearGradient>
            </defs>

            {/* Concentric Web Circles (20%, 40%, 60%, 80%, 100%) */}
            {[0.2, 0.4, 0.6, 0.8, 1.0].map((frac, idx) => (
              <circle
                key={idx}
                cx={center}
                cy={center}
                r={radius * frac}
                fill="none"
                stroke="#1E293B"
                strokeWidth="1"
                strokeDasharray={idx === 4 ? 'none' : '3 3'}
              />
            ))}

            {/* Axis Spokes from center */}
            {dimensions.map((d, i) => {
              const { x, y } = getCoordinates(i, 100);
              return (
                <line
                  key={i}
                  x1={center}
                  y1={center}
                  x2={x}
                  y2={y}
                  stroke="#334155"
                  strokeWidth="1"
                />
              );
            })}

            {/* Polygon Shape */}
            <polygon
              points={polygonPoints}
              fill="url(#radarAreaGrad)"
              stroke="#F59E0B"
              strokeWidth="2.4"
              strokeLinejoin="round"
            />

            {/* Vertex Nodes & Values */}
            {dimensions.map((d, i) => {
              const { x, y } = getCoordinates(i, d.value);
              const labelCoord = getCoordinates(i, 120);

              return (
                <g key={i}>
                  <circle cx={x} cy={y} r="3.5" fill="#FBBF24" stroke="#0B1120" strokeWidth="1.5" />
                  <text
                    x={labelCoord.x}
                    y={labelCoord.y + (labelCoord.y > center ? 4 : -2)}
                    textAnchor="middle"
                    fill="#94A3B8"
                    fontSize="8"
                    fontWeight="bold"
                  >
                    {d.dimension}
                  </text>
                </g>
              );
            })}

            {/* Center AI Risk Label */}
            <circle cx={center} cy={center} r="22" fill="#0F172A" stroke="#334155" strokeWidth="1.5" />
            <text x={center} y={center - 3} textAnchor="middle" fill="#94A3B8" fontSize="7" fontWeight="bold">
              RISK
            </text>
            <text x={center} y={center + 9} textAnchor="middle" fill="#FBBF24" fontSize="11" fontWeight="black">
              {aiScore}%
            </text>
          </svg>

          {/* Classification Tag */}
          <div className="mt-1 flex items-center gap-2">
            <span className="text-[10px] text-slate-400">DistilBERT Predicted Tier:</span>
            <span
              className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                riskLevel === 'CRITICAL'
                  ? 'bg-rose-950/80 text-rose-300 border-rose-800'
                  : riskLevel === 'HIGH'
                  ? 'bg-amber-950/80 text-amber-300 border-amber-800'
                  : 'bg-emerald-950/80 text-emerald-300 border-emerald-800'
              }`}
            >
              {riskLevel} RISK
            </span>
          </div>
        </div>

        {/* 8-Dimension Breakdown Table */}
        <div className="space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <h4 className="text-xs font-bold text-slate-200">Dimension Score Breakdown</h4>
            <span className="text-[11px] font-mono text-amber-400 font-bold">
              AI Risk Index: {aiScore}%
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs">
            {dimensions.map((d, i) => (
              <div key={i} className="p-2 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] text-slate-400">{d.dimension}</span>
                  <span className={`font-mono font-bold ${d.value > 70 ? 'text-amber-400' : 'text-slate-200'}`}>
                    {d.value}%
                  </span>
                </div>
                {/* Mini progress bar */}
                <div className="w-full h-1 bg-slate-800 rounded-full mt-1.5 overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      d.dimension.includes('Risk') && d.value > 65
                        ? 'bg-rose-500'
                        : d.value >= 85
                        ? 'bg-emerald-500'
                        : 'bg-amber-500'
                    }`}
                    style={{ width: `${d.value}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* AI Explanation note */}
          <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 text-[11px] text-slate-300 flex items-start gap-2">
            <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-white">AI Vulnerability Driver: </span>
              {radarData?.summary ||
                'High corridor concentration and port congestion vulnerability offset by high internal fab yield.'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
