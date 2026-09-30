import React from 'react';
import { FileText } from 'lucide-react';
import Button from '../ui/Button';

export default function DocumentStatus({ data, onManageDocs }) {
  const { verified, pending, rejected, total } = data;

  // Donut chart math
  const radius = 38;
  const circumference = 2 * Math.PI * radius;

  const verifiedPercent = verified / total;
  const pendingPercent = pending / total;
  const rejectedPercent = rejected / total;

  const verifiedStroke = verifiedPercent * circumference;
  const pendingStroke = pendingPercent * circumference;
  const rejectedStroke = rejectedPercent * circumference;

  // Offsets for stroke-dashoffset
  const verifiedOffset = 0;
  const pendingOffset = -verifiedStroke;
  const rejectedOffset = -(verifiedStroke + pendingStroke);

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs p-5 sm:p-6 flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-emerald-50 text-emerald-600 border border-emerald-100">
              <FileText className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 leading-none">
                Document Status
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                KYC, Deeds & Certification vault
              </p>
            </div>
          </div>

          <Button
            variant="ghost"
            size="xs"
            onClick={onManageDocs}
            className="text-xs font-semibold text-blue-600 hover:text-blue-700"
          >
            Manage
          </Button>
        </div>

        {/* SVG Donut Chart */}
        <div className="relative my-6 flex items-center justify-center">
          <svg className="w-36 h-36 transform -rotate-90" viewBox="0 0 100 100">
            {/* Background ring */}
            <circle
              cx="50"
              cy="50"
              r={radius}
              className="text-slate-100"
              strokeWidth="10"
              stroke="currentColor"
              fill="transparent"
            />
            {/* Verified (Green) */}
            <circle
              cx="50"
              cy="50"
              r={radius}
              className="text-emerald-500 transition-all duration-700 ease-out"
              strokeWidth="10"
              strokeDasharray={`${verifiedStroke} ${circumference}`}
              strokeDashoffset={verifiedOffset}
              strokeLinecap="round"
              stroke="currentColor"
              fill="transparent"
            />
            {/* Pending (Orange) */}
            <circle
              cx="50"
              cy="50"
              r={radius}
              className="text-amber-500 transition-all duration-700 ease-out"
              strokeWidth="10"
              strokeDasharray={`${pendingStroke} ${circumference}`}
              strokeDashoffset={pendingOffset}
              strokeLinecap="round"
              stroke="currentColor"
              fill="transparent"
            />
            {/* Rejected (Red) */}
            <circle
              cx="50"
              cy="50"
              r={radius}
              className="text-rose-500 transition-all duration-700 ease-out"
              strokeWidth="10"
              strokeDasharray={`${rejectedStroke} ${circumference}`}
              strokeDashoffset={rejectedOffset}
              strokeLinecap="round"
              stroke="currentColor"
              fill="transparent"
            />
          </svg>

          {/* Center Info in Donut */}
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
            <span className="text-2xl font-extrabold text-slate-900 leading-none">
              {total}
            </span>
            <span className="text-[11px] font-medium text-slate-400 mt-1 uppercase tracking-wider">
              Total Files
            </span>
          </div>
        </div>

        {/* Legend */}
        <div className="space-y-2 pt-2 border-t border-slate-100">
          <div className="flex items-center justify-between text-xs py-1 px-2 rounded-lg hover:bg-slate-50 transition-colors">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 ring-2 ring-emerald-100" />
              <span className="font-medium text-slate-700">Verified</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-900">{verified}</span>
              <span className="text-[11px] text-slate-400">
                ({Math.round(verifiedPercent * 100)}%)
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between text-xs py-1 px-2 rounded-lg hover:bg-slate-50 transition-colors">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500 ring-2 ring-amber-100" />
              <span className="font-medium text-slate-700">Pending</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-900">{pending}</span>
              <span className="text-[11px] text-slate-400">
                ({Math.round(pendingPercent * 100)}%)
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between text-xs py-1 px-2 rounded-lg hover:bg-slate-50 transition-colors">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500 ring-2 ring-rose-100" />
              <span className="font-medium text-slate-700">Rejected</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-900">{rejected}</span>
              <span className="text-[11px] text-slate-400">
                ({Math.round(rejectedPercent * 100)}%)
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
