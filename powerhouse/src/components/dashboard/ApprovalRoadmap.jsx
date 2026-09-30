import React from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  Building,
  ChevronRight
} from 'lucide-react';
import Badge from '../ui/Badge';
import Button from '../ui/Button';

export default function ApprovalRoadmap({ steps, onViewFullRoadmap }) {
  const getStepIcon = (status, stepNumber) => {
    switch (status) {
      case 'Completed':
        return (
          <div className="w-8 h-8 rounded-full bg-emerald-500 text-white flex items-center justify-center shadow-xs ring-4 ring-emerald-50 font-bold text-xs">
            <CheckCircle2 className="w-4 h-4" />
          </div>
        );
      case 'In Progress':
        return (
          <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center shadow-xs ring-4 ring-blue-50 font-bold text-xs">
            <span>{stepNumber}</span>
          </div>
        );
      case 'Pending':
      default:
        return (
          <div className="w-8 h-8 rounded-full bg-amber-500 text-white flex items-center justify-center shadow-xs ring-4 ring-amber-50 font-bold text-xs">
            <span>{stepNumber}</span>
          </div>
        );
    }
  };

  const getLineStyle = (status) => {
    switch (status) {
      case 'Completed':
        return 'bg-emerald-500';
      case 'In Progress':
        return 'bg-blue-400';
      default:
        return 'bg-slate-200';
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs p-5 sm:p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-5 border-b border-slate-100">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-blue-50 text-blue-600 border border-blue-100">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-base sm:text-lg font-bold text-slate-900 leading-none">
              Verified Approval Roadmap
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Custom sequential compliance pipeline based on your business sector & capacity.
            </p>
          </div>
        </div>

        <Button
          variant="secondary"
          size="sm"
          onClick={onViewFullRoadmap}
          className="self-start sm:self-auto text-xs font-semibold text-blue-600 hover:text-blue-700"
        >
          <span>View Full Roadmap</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </Button>
      </div>

      {/* Roadmap Vertical Pipeline */}
      <div className="mt-6 flow-root">
        <div className="relative">
          {steps.map((item, index) => {
            const isLast = index === steps.length - 1;

            return (
              <div key={item.step} className="relative pb-6 last:pb-0 group">
                {/* Connecting Line */}
                {!isLast && (
                  <span
                    className={`absolute top-8 left-4 -ml-px h-full w-0.5 ${getLineStyle(
                      item.status
                    )} transition-colors`}
                    aria-hidden="true"
                  />
                )}

                <div className="relative flex items-start gap-4">
                  {/* Step Indicator */}
                  <div className="shrink-0 flex items-center justify-center">
                    {getStepIcon(item.status, item.step)}
                  </div>

                  {/* Step Card Content */}
                  <div className="flex-1 min-w-0 bg-slate-50/70 group-hover:bg-slate-50 border border-slate-200/70 group-hover:border-slate-300 rounded-xl p-3.5 sm:p-4 transition-all duration-150 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                          STEP {item.step}
                        </span>
                        <span className="text-xs font-semibold text-slate-900 group-hover:text-blue-600 transition-colors truncate">
                          {item.title}
                        </span>
                        {item.category && (
                          <span className="text-[10px] px-2 py-0.5 rounded-md bg-white text-slate-600 border border-slate-200 font-medium">
                            {item.category}
                          </span>
                        )}
                      </div>

                      <div className="mt-1 flex items-center gap-1.5 text-xs text-slate-500">
                        <Building className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span className="font-medium text-slate-600">
                          Authority:
                        </span>
                        <span className="truncate">{item.authority}</span>
                      </div>

                      {item.estimatedDays && (
                        <div className="text-[11px] text-slate-400 mt-1">
                          {item.estimatedDays}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-3 shrink-0 self-start sm:self-center">
                      <Badge variant={item.status} withDot>
                        {item.status}
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
