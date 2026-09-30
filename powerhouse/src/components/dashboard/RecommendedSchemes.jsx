import React from 'react';
import {
  Landmark,
  TrendingUp,
  ChevronRight,
  ArrowRight,
  Gift
} from 'lucide-react';
import Button from '../ui/Button';

const iconMap = {
  Landmark,
  TrendingUp,
};

export default function RecommendedSchemes({ schemes, onViewAll, onSchemeDetails }) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs p-5 sm:p-6 flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-blue-50 text-blue-600 border border-blue-100">
              <Gift className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 leading-none">
                Recommended Schemes
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Subsidies matched to your profile
              </p>
            </div>
          </div>

          <Button
            variant="secondary"
            size="sm"
            onClick={onViewAll}
            className="text-xs font-semibold text-blue-600 hover:text-blue-700"
          >
            <span>View All</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Button>
        </div>

        {/* Scheme Cards */}
        <div className="mt-4 space-y-3">
          {schemes.map((scheme) => {
            const Icon = iconMap[scheme.icon] || Landmark;

            return (
              <div
                key={scheme.id}
                className="group p-4 rounded-xl border border-slate-200/80 bg-slate-50/50 hover:bg-white hover:border-blue-200 hover:shadow-xs transition-all duration-200 flex flex-col justify-between gap-3"
              >
                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-lg bg-blue-600/10 text-blue-600 flex items-center justify-center shrink-0 border border-blue-200/50 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                    <Icon className="w-4 h-4" />
                  </div>

                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-2">
                      <h3 className="text-xs sm:text-sm font-bold text-slate-900 group-hover:text-blue-600 transition-colors truncate">
                        {scheme.title}
                      </h3>
                      {scheme.badge && (
                        <span className="text-[10px] font-semibold text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded border border-blue-100 shrink-0">
                          {scheme.badge}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-500 mt-1 line-clamp-2 leading-relaxed">
                      {scheme.description}
                    </p>
                  </div>
                </div>

                <div className="pt-2.5 border-t border-slate-200/60 flex items-center justify-between gap-2">
                  <div className="flex items-center gap-1.5">
                    <span className="text-[11px] font-medium text-slate-500">
                      Benefit:
                    </span>
                    <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
                      {scheme.benefit}
                    </span>
                  </div>

                  <button
                    type="button"
                    onClick={() => onSchemeDetails(scheme)}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800 transition-colors cursor-pointer"
                  >
                    <span>View Details</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
