import React, { useState } from 'react';
import {
  Layers,
  Info,
  Maximize2,
  RefreshCw,
  Anchor,
  Factory,
  Warehouse as WarehouseIcon,
  Truck,
  Users,
  AlertTriangle,
  CheckCircle2,
  Activity,
} from 'lucide-react';

const NODE_ICONS = {
  supplier: Factory,
  port: Anchor,
  warehouse: WarehouseIcon,
  factory: Layers,
  customer: Users,
};

const STATUS_COLORS = {
  healthy: {
    bg: '#064E3B',
    border: '#059669',
    text: '#34D399',
    glow: 'rgba(16, 185, 129, 0.4)',
    badge: 'bg-emerald-950/80 text-emerald-300 border-emerald-800',
  },
  warning: {
    bg: '#78350F',
    border: '#D97706',
    text: '#FBBF24',
    glow: 'rgba(245, 158, 11, 0.4)',
    badge: 'bg-amber-950/80 text-amber-300 border-amber-800',
  },
  critical: {
    bg: '#7F1D1D',
    border: '#DC2626',
    text: '#F87171',
    glow: 'rgba(239, 68, 68, 0.5)',
    badge: 'bg-rose-950/80 text-rose-300 border-rose-800',
  },
  disrupted: {
    bg: '#4C0519',
    border: '#E11D48',
    text: '#FB7185',
    glow: 'rgba(244, 63, 94, 0.6)',
    badge: 'bg-rose-950/90 text-rose-200 border-rose-700 animate-pulse',
  },
  alternate: {
    bg: '#083344',
    border: '#0891B2',
    text: '#38BDF8',
    glow: 'rgba(14, 165, 233, 0.5)',
    badge: 'bg-cyan-950/80 text-cyan-300 border-cyan-800',
  },
};

export default function NetworkGraphMap({ networkData, onSelectNode }) {
  const [selectedNodeId, setSelectedNodeId] = useState('PORT_KAOHSIUNG');
  const [filterType, setFilterType] = useState('ALL');

  const nodes = networkData?.nodes || [];
  const edges = networkData?.edges || [];

  const filteredNodes = filterType === 'ALL' ? nodes : nodes.filter((n) => n.type === filterType.toLowerCase());
  const selectedNode = nodes.find((n) => n.id === selectedNodeId) || nodes[0];

  const handleNodeClick = (node) => {
    setSelectedNodeId(node.id);
    if (onSelectNode) onSelectNode(node);
  };

  return (
    <div className="bg-[#111827] rounded-2xl border border-[#1E293B] overflow-hidden flex flex-col">
      {/* Header Controls */}
      <div className="p-4 border-b border-[#1E293B] flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-cyan-950/60 border border-cyan-800/60 flex items-center justify-center text-cyan-400">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              Supply Network Topology Graph
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-800/60 font-mono">
                LIVE TELEMETRY
              </span>
            </h3>
            <p className="text-[11px] text-slate-400">
              Interactive multi-echelon flow: Supplier → Port → DC → Factory → Customer
            </p>
          </div>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {['ALL', 'SUPPLIER', 'PORT', 'WAREHOUSE', 'FACTORY'].map((f) => (
            <button
              key={f}
              onClick={() => setFilterType(f)}
              className={`px-2.5 py-1 rounded-lg text-[10px] font-semibold tracking-wider transition-colors cursor-pointer ${
                filterType === f
                  ? 'bg-cyan-900/60 text-cyan-300 border border-cyan-700'
                  : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* SVG Canvas & Node Inspector split */}
      <div className="grid grid-cols-1 lg:grid-cols-4 min-h-[460px]">
        {/* SVG Interactive Canvas */}
        <div className="lg:col-span-3 relative bg-[#0B1120] p-4 flex items-center justify-center overflow-x-auto scrollbar-thin">
          <svg
            viewBox="0 0 920 480"
            className="w-full h-auto min-w-[720px] max-w-[920px] select-none"
            style={{ filter: 'drop-shadow(0 4px 12px rgba(0,0,0,0.5))' }}
          >
            <defs>
              <linearGradient id="healthyGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#059669" />
                <stop offset="100%" stopColor="#047857" />
              </linearGradient>
              <linearGradient id="disruptedGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#E11D48" />
                <stop offset="100%" stopColor="#BE123C" />
              </linearGradient>
              <linearGradient id="altGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#0284C7" />
                <stop offset="100%" stopColor="#0369A1" />
              </linearGradient>

              {/* Marker Arrows */}
              <marker id="arrow-healthy" viewBox="0 0 10 10" refX="24" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#10B981" />
              </marker>
              <marker id="arrow-disrupted" viewBox="0 0 10 10" refX="24" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#F43F5E" />
              </marker>
              <marker id="arrow-alt" viewBox="0 0 10 10" refX="24" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#38BDF8" />
              </marker>
              <marker id="arrow-warning" viewBox="0 0 10 10" refX="24" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#F59E0B" />
              </marker>
            </defs>

            {/* Grid Backdrop Lines */}
            <g stroke="#1E293B" strokeWidth="0.5" strokeDasharray="4 4" opacity="0.4">
              <line x1="185" y1="20" x2="185" y2="460" />
              <line x1="365" y1="20" x2="365" y2="460" />
              <line x1="550" y1="20" x2="550" y2="460" />
              <line x1="730" y1="20" x2="730" y2="460" />
            </g>

            {/* Column Headers */}
            <text x="100" y="32" textAnchor="middle" fill="#64748B" fontSize="10" fontWeight="700" letterSpacing="1">
              SUPPLIERS
            </text>
            <text x="270" y="32" textAnchor="middle" fill="#64748B" fontSize="10" fontWeight="700" letterSpacing="1">
              PORTS / HUBS
            </text>
            <text x="460" y="32" textAnchor="middle" fill="#64748B" fontSize="10" fontWeight="700" letterSpacing="1">
              WAREHOUSES / DCS
            </text>
            <text x="640" y="32" textAnchor="middle" fill="#64748B" fontSize="10" fontWeight="700" letterSpacing="1">
              FACTORIES
            </text>
            <text x="820" y="32" textAnchor="middle" fill="#64748B" fontSize="10" fontWeight="700" letterSpacing="1">
              CUSTOMERS
            </text>

            {/* Render Edges */}
            {edges.map((edge) => {
              const sNode = nodes.find((n) => n.id === edge.source);
              const tNode = nodes.find((n) => n.id === edge.target);
              if (!sNode || !tNode) return null;

              const isDisrupted = edge.status === 'disrupted';
              const isAlt = edge.status === 'alternate';
              const isWarning = edge.status === 'warning';

              const strokeColor = isDisrupted ? '#F43F5E' : isAlt ? '#38BDF8' : isWarning ? '#F59E0B' : '#10B981';
              const markerEnd = isDisrupted
                ? 'url(#arrow-disrupted)'
                : isAlt
                ? 'url(#arrow-alt)'
                : isWarning
                ? 'url(#arrow-warning)'
                : 'url(#arrow-healthy)';

              // Compute Bezier control points
              const dx = (tNode.x - sNode.x) * 0.5;
              const pathD = `M ${sNode.x} ${sNode.y} C ${sNode.x + dx} ${sNode.y}, ${tNode.x - dx} ${tNode.y}, ${tNode.x} ${tNode.y}`;

              return (
                <g key={edge.id} className="transition-opacity hover:opacity-100">
                  <path
                    d={pathD}
                    fill="none"
                    stroke={strokeColor}
                    strokeWidth={isDisrupted ? '3' : isAlt ? '2.5' : '1.8'}
                    strokeDasharray={isAlt ? '6 4' : isDisrupted ? '4 4' : 'none'}
                    markerEnd={markerEnd}
                    opacity={isDisrupted ? '0.9' : '0.65'}
                  />
                  {/* Midpoint Label */}
                  {edge.label && (
                    <text
                      x={(sNode.x + tNode.x) / 2}
                      y={(sNode.y + tNode.y) / 2 - 6}
                      fill={strokeColor}
                      fontSize="8"
                      fontWeight="bold"
                      textAnchor="middle"
                      className="bg-slate-900/80 px-1 py-0.5"
                    >
                      {edge.label}
                    </text>
                  )}
                </g>
              );
            })}

            {/* Render Nodes */}
            {filteredNodes.map((node) => {
              const colors = STATUS_COLORS[node.status] || STATUS_COLORS.healthy;
              const isSelected = node.id === selectedNodeId;

              return (
                <g
                  key={node.id}
                  transform={`translate(${node.x}, ${node.y})`}
                  onClick={() => handleNodeClick(node)}
                  className="cursor-pointer group"
                >
                  {/* Selection Pulse Ring */}
                  {isSelected && (
                    <circle
                      r="26"
                      fill="none"
                      stroke={colors.border}
                      strokeWidth="2"
                      opacity="0.8"
                      className="animate-ping"
                      style={{ transformOrigin: '0 0' }}
                    />
                  )}

                  {/* Node Outer Circle */}
                  <circle
                    r="20"
                    fill={colors.bg}
                    stroke={isSelected ? '#FFFFFF' : colors.border}
                    strokeWidth={isSelected ? '3' : '2'}
                    style={{
                      filter: isSelected ? `drop-shadow(0 0 10px ${colors.glow})` : undefined,
                    }}
                  />

                  {/* Status Indicator Pip */}
                  <circle
                    cx="14"
                    cy="-14"
                    r="5"
                    fill={colors.text}
                    stroke="#0B1120"
                    strokeWidth="1.5"
                  />

                  {/* Node Name */}
                  <text
                    y="32"
                    textAnchor="middle"
                    fill={isSelected ? '#FFFFFF' : '#CBD5E1'}
                    fontSize="9"
                    fontWeight="700"
                  >
                    {node.name.length > 18 ? node.name.slice(0, 16) + '..' : node.name}
                  </text>

                  {/* Node Region Subtitle */}
                  <text
                    y="42"
                    textAnchor="middle"
                    fill="#94A3B8"
                    fontSize="7.5"
                  >
                    {node.region}
                  </text>
                </g>
              );
            })}
          </svg>

          {/* Floating Legend */}
          <div className="absolute bottom-3 left-4 bg-slate-950/85 backdrop-blur-md border border-slate-800 rounded-xl p-2.5 flex items-center gap-3 text-[10px]">
            <span className="flex items-center gap-1.5 text-emerald-400">
              <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" /> Healthy
            </span>
            <span className="flex items-center gap-1.5 text-amber-400">
              <span className="w-2 h-2 rounded-full bg-amber-500 inline-block" /> Warning
            </span>
            <span className="flex items-center gap-1.5 text-rose-400">
              <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse inline-block" /> Disrupted
            </span>
            <span className="flex items-center gap-1.5 text-cyan-400">
              <span className="w-2 h-2 rounded-full bg-cyan-400 inline-block" /> AI Bypass
            </span>
          </div>
        </div>

        {/* Selected Node Inspector Drawer */}
        <div className="p-5 border-t lg:border-t-0 lg:border-l border-[#1E293B] bg-[#111827] flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                Node Inspector
              </span>
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                  STATUS_COLORS[selectedNode?.status]?.badge || 'bg-slate-800 text-slate-300'
                }`}
              >
                {selectedNode?.status?.toUpperCase()}
              </span>
            </div>

            <div>
              <h4 className="text-base font-bold text-white">{selectedNode?.name}</h4>
              <p className="text-xs text-slate-400">{selectedNode?.region}</p>
            </div>

            <div className="space-y-2 pt-2 border-t border-slate-800 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Node Type</span>
                <span className="font-semibold text-slate-200 capitalize">{selectedNode?.type}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">AI Risk Assessment</span>
                <span
                  className={`font-bold ${
                    selectedNode?.risk === 'Critical'
                      ? 'text-rose-400'
                      : selectedNode?.risk === 'High'
                      ? 'text-amber-400'
                      : 'text-emerald-400'
                  }`}
                >
                  {selectedNode?.risk}
                </span>
              </div>
              <div className="flex flex-col gap-1 pt-1">
                <span className="text-slate-400">Flow / Material Telemetry</span>
                <span className="font-mono text-[11px] text-cyan-300 bg-slate-900/90 p-2 rounded-lg border border-slate-800">
                  {selectedNode?.prods || 'Standard corridor transit load'}
                </span>
              </div>
            </div>

            {selectedNode?.status === 'disrupted' && (
              <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-800/60 text-xs space-y-1">
                <div className="flex items-center gap-1.5 text-rose-300 font-bold">
                  <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                  <span>Active Disruption Detected</span>
                </div>
                <p className="text-[11px] text-rose-200/80">
                  Typhoon Gaemi swell has closed 3 berths. AI reroute option generated via Port of Busan.
                </p>
              </div>
            )}
          </div>

          <div className="pt-2 text-[10px] text-slate-500 border-t border-slate-800 flex items-center gap-1">
            <Info className="w-3 h-3 text-slate-400 shrink-0" />
            <span>Click any node in graph to inspect live telemetry</span>
          </div>
        </div>
      </div>
    </div>
  );
}
