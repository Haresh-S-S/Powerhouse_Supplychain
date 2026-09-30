import React from 'react';
import { CheckCircle2, AlertCircle, Shield } from 'lucide-react';
import { profileStatusChecklist } from '../../data/businessProfileData';

export default function ProfileStatus({ checklist = profileStatusChecklist, completionPercentage = 85 }) {
  return (
    <div className="bg-[#111827] rounded-2xl border border-[#1E293B] p-5 sm:p-6">
      <div className="flex items-center gap-2.5 pb-4 border-b border-slate-800">
        <div className="p-1.5 rounded-lg bg-blue-900/30 text-blue-400 border border-blue-800/50">
          <Shield className="w-4 h-4" />
        </div>
        <div>
          <h3 className="text-base font-bold text-slate-100 leading-none">
            Profile Status
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Section completion checklist
          </p>
        </div>
      </div>

      <div className="mt-4 space-y-2.5">
        {checklist.map((item) => {
          const isDone = item.status === 'Completed';

          return (
            <div
              key={item.id}
              className="flex items-center justify-between py-1.5 px-2 rounded-lg hover:bg-[#141C2B] transition-colors"
            >
              <div className="flex items-center gap-2">
                {isDone ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
                )}
                <span className="text-xs font-medium text-slate-300">
                  {item.label}
                </span>
              </div>

              <span
                className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${
                  isDone
                    ? 'bg-emerald-950/40 text-emerald-400 border-emerald-800/50'
                    : 'bg-amber-950/40 text-amber-400 border-amber-800/50'
                }`}
              >
                {item.status}
              </span>
            </div>
          );
        })}
      </div>

      {/* Progress Footer */}
      <div className="mt-5 pt-4 border-t border-slate-800 space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="font-semibold text-slate-400">Profile Completion</span>
          <span className="font-bold text-blue-400">{completionPercentage}%</span>
        </div>
        <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-600 rounded-full transition-all duration-500"
            style={{ width: `${completionPercentage}%` }}
          />
        </div>
      </div>
    </div>
  );
}