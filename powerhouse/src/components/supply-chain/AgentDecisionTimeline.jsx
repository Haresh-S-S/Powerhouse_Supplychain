import React, { useState } from 'react';
import {
  Clock,
  Shield,
  CheckCircle2,
  AlertTriangle,
  Bot,
  UserCheck,
  Search,
  Filter,
  Layers,
  Cpu,
} from 'lucide-react';

const AGENT_BADGES = {
  'Disruption Agent': { bg: 'bg-rose-950/80', border: 'border-rose-800', text: 'text-rose-400' },
  'Scenario Agent': { bg: 'bg-indigo-950/80', border: 'border-indigo-800', text: 'text-indigo-400' },
  'Logistics Agent': { bg: 'bg-blue-950/80', border: 'border-blue-800', text: 'text-blue-400' },
  'Inventory Agent': { bg: 'bg-cyan-950/80', border: 'border-cyan-800', text: 'text-cyan-400' },
  'Human Approval Gate': { bg: 'bg-emerald-950/80', border: 'border-emerald-800', text: 'text-emerald-400' },
  'Supplier Risk Engine': { bg: 'bg-amber-950/80', border: 'border-amber-800', text: 'text-amber-400' },
};

export default function AgentDecisionTimeline({ auditRecords = [] }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAgent, setSelectedAgent] = useState('ALL');

  const filtered = auditRecords.filter((a) => {
    const matchesSearch =
      a.action?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.reason?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.agent_name?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesAgent = selectedAgent === 'ALL' || a.agent_name?.toLowerCase().includes(selectedAgent.toLowerCase());
    return matchesSearch && matchesAgent;
  });

  return (
    <div className="bg-[#111827] rounded-2xl border border-[#1E293B] p-5 space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold text-white">Agent Activity & Decision Timeline</h3>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-mono">
              Immutable Audit Trail
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Step-by-step agent telemetry, reason codes, confidence ratings, and human gate sign-offs
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
            <input
              type="text"
              placeholder="Search actions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-slate-900 text-xs text-slate-200 pl-8 pr-3 py-1.5 rounded-xl border border-slate-800 focus:outline-none focus:border-cyan-500 w-36 sm:w-48"
            />
          </div>

          <select
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
            className="bg-slate-900 text-xs text-slate-200 border border-slate-700 rounded-xl px-2.5 py-1.5 focus:outline-none focus:border-cyan-500 cursor-pointer"
          >
            <option value="ALL">All Agents</option>
            <option value="Disruption">Disruption Agent</option>
            <option value="Scenario">Scenario Agent</option>
            <option value="Logistics">Logistics Agent</option>
            <option value="Inventory">Inventory Agent</option>
            <option value="Human">Human Gate</option>
          </select>
        </div>
      </div>

      {/* Timeline Stream */}
      <div className="relative border-l border-slate-800 ml-4 space-y-6 pt-2">
        {filtered.map((record, idx) => {
          const badge =
            Object.entries(AGENT_BADGES).find(([k]) => record.agent_name?.includes(k))?.[1] ||
            AGENT_BADGES['Disruption Agent'];

          const isHuman = record.agent_name?.includes('Human');

          return (
            <div key={idx} className="relative pl-6 group">
              {/* Timeline Marker Dot */}
              <div
                className={`absolute -left-[9px] top-1 w-4 h-4 rounded-full border-2 bg-[#0B1120] flex items-center justify-center ${
                  isHuman ? 'border-emerald-500 text-emerald-400' : 'border-cyan-500 text-cyan-400'
                }`}
              >
                {isHuman ? <UserCheck className="w-2.5 h-2.5" /> : <Bot className="w-2.5 h-2.5" />}
              </div>

              {/* Event Content Card */}
              <div className="p-3.5 rounded-xl bg-[#0B1120] border border-slate-800/80 hover:border-slate-700 transition-colors space-y-2">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${badge.bg} ${badge.border} ${badge.text}`}>
                      {record.agent_name}
                    </span>
                    <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
                      <Clock className="w-3 h-3 text-slate-500" />
                      {record.timestamp}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    {record.approval_required && (
                      <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-800">
                        GATE REQUIRED
                      </span>
                    )}
                    <span
                      className={`text-[9px] font-bold px-2 py-0.5 rounded uppercase font-mono ${
                        record.decision === 'APPROVED'
                          ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                          : record.decision === 'REJECTED'
                          ? 'bg-rose-950 text-rose-400 border border-rose-800'
                          : 'bg-slate-800 text-cyan-300 border border-slate-700'
                      }`}
                    >
                      {record.decision}
                    </span>
                  </div>
                </div>

                <h4 className="text-xs font-bold text-white">{record.action}</h4>
                <p className="text-[11px] text-slate-300 leading-relaxed">{record.reason}</p>

                {/* Telemetry metadata tags */}
                {record.data_used && Object.keys(record.data_used).length > 0 && (
                  <div className="pt-1.5 border-t border-slate-800/60 flex items-center gap-3 text-[10px] text-slate-400 flex-wrap">
                    <span className="font-semibold text-slate-400">Data Used:</span>
                    {Object.entries(record.data_used).map(([k, v], i) => (
                      <span key={i} className="font-mono text-slate-300 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
                        {k}: {typeof v === 'object' ? JSON.stringify(v).slice(0, 25) + '..' : String(v)}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {filtered.length === 0 && (
          <div className="p-8 text-center text-xs text-slate-500">
            No audit records matching filter.
          </div>
        )}
      </div>
    </div>
  );
}
