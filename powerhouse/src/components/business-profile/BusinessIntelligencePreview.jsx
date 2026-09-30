import React from 'react';
import { BrainCircuit, ArrowRight, FileCheck, Gift, CalendarClock, RefreshCw } from 'lucide-react';
import Button from '../ui/Button';
import { useBusinessAnalysis } from '../../context/BusinessAnalysisContext';

export default function BusinessIntelligencePreview({ onViewAnalysis, isAnalyzing = false }) {
  const { analysisResult } = useBusinessAnalysis();

  const approvalsCount = analysisResult?.summary?.totalApprovals || 12;
  const schemesCount = analysisResult?.summary?.recommendedSchemes || 8;
  const tasksCount = analysisResult?.summary?.upcomingTasks || 5;

  const insights = [
    {
      value: approvalsCount.toString(),
      label: 'Potential Approvals Identified',
      icon: FileCheck,
      color: 'text-blue-600 bg-blue-50 border-blue-100',
    },
    {
      value: schemesCount.toString(),
      label: 'Relevant Government Schemes',
      icon: Gift,
      color: 'text-emerald-600 bg-emerald-50 border-emerald-100',
    },
    {
      value: tasksCount.toString(),
      label: 'Upcoming Compliance Requirements',
      icon: CalendarClock,
      color: 'text-amber-600 bg-amber-50 border-amber-100',
    },
  ];

  return (
    <div className="bg-[#111827] rounded-2xl border border-[#1E293B] p-5 sm:p-6 flex flex-col justify-between">
      <div>
        <div className="flex items-center gap-2.5 pb-4 border-b border-slate-800">
          <div className="p-1.5 rounded-lg bg-blue-900/30 text-blue-400 border border-blue-800/50">
            <BrainCircuit className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100 leading-none">
              Business Intelligence Preview
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Deterministic regulatory discovery engine
            </p>
          </div>
        </div>

        <p className="text-xs text-slate-400 leading-relaxed mt-4">
          Based on your business profile, POWER HOUSE can analyze your compliance and approval requirements.
        </p>

        {/* 3 Insight Metrics */}
        <div className="mt-4 space-y-2.5">
          {insights.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div
                key={idx}
                className="p-3 rounded-xl bg-[#141C2B] border border-[#1E293B] flex items-center justify-between gap-3 group hover:border-slate-700 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-8 h-8 rounded-lg flex items-center justify-center border ${item.color} shrink-0`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="text-xs font-semibold text-slate-300 leading-tight">
                    {item.label}
                  </span>
                </div>
                <span className="text-lg font-extrabold text-slate-100 shrink-0">
                  {item.value}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-5 pt-4 border-t border-slate-800">
        <Button
          variant="primary"
          size="sm"
          onClick={onViewAnalysis}
          disabled={isAnalyzing}
          className="w-full text-xs font-semibold"
        >
          {isAnalyzing ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span>Analyzing Profile...</span>
            </>
          ) : (
            <>
              <BrainCircuit className="w-3.5 h-3.5" />
              <span>View Business Analysis</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </>
          )}
        </Button>
      </div>
    </div>
  );
}