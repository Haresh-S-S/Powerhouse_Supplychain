import React from 'react';
import { ArrowRight, ShieldCheck } from 'lucide-react';
import Button from '../ui/Button';

export default function ProfileCompletion({ onCompleteClick, completionPercentage = 85, remainingItems = 2 }) {
  return (
    <div className="relative overflow-hidden bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 rounded-2xl p-5 sm:p-6 border border-slate-700/80 shadow-md text-white">
      {/* Subtle Background Glow */}
      <div className="absolute -right-10 -top-10 w-48 h-48 bg-blue-500/10 rounded-full blur-2xl pointer-events-none" />

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
        <div className="max-w-xl space-y-2">
          <div className="flex items-center gap-2">
            <span className="p-1 rounded-md bg-blue-500/20 text-blue-400 border border-blue-400/30">
              <ShieldCheck className="w-3.5 h-3.5" />
            </span>
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-400">
              Action Required
            </span>
          </div>

          <h2 className="text-lg sm:text-xl font-bold tracking-tight text-white">
            Complete Your Business Profile
          </h2>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            Keep your business information up to date to receive accurate compliance and approval recommendations.
          </p>

          {/* Progress Bar Area */}
          <div className="pt-2 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-200">
                Profile Completion
              </span>
              <span className="font-bold text-blue-400">
                {completionPercentage}% Complete
              </span>
            </div>

            <div className="w-full h-2.5 bg-slate-700/80 rounded-full overflow-hidden p-0.5 border border-slate-600/50">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full transition-all duration-700 ease-out"
                style={{ width: `${completionPercentage}%` }}
              />
            </div>

            <div className="text-[11px] text-slate-400 font-medium flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
              <span>{remainingItems} details remaining (Financial details & Environmental classification)</span>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="shrink-0 self-start md:self-center">
          <Button
            variant="primary"
            size="md"
            onClick={onCompleteClick}
            className="bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-lg shadow-blue-900/40 border border-blue-400/30"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Complete Profile</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>
    </div>
  );
}