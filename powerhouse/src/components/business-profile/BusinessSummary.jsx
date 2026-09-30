import React from 'react';
import {
  Briefcase,
  Factory,
  MapPin,
  Users,
  Calendar,
  Building2
} from 'lucide-react';

export default function BusinessSummary({ data }) {
  const summaryRows = [
    { label: 'Industry', value: data.industry, icon: Factory },
    { label: 'Location', value: data.operatingLocation || `${data.city}, ${data.state}`, icon: MapPin },
    { label: 'Business Size', value: data.companySize, icon: Briefcase },
    { label: 'Employees', value: `${data.employees} Staff`, icon: Users },
    { label: 'Operating Since', value: data.establishedDate || '2018', icon: Calendar },
  ];

  return (
    <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-5 sm:p-6">
      <div className="flex items-center gap-2.5 pb-4 border-b border-slate-800">
        <div className="p-1.5 rounded-lg bg-blue-950 text-blue-400 border border-blue-800">
          <Building2 className="w-4 h-4" />
        </div>
        <div>
          <h3 className="text-base font-bold text-white leading-none">
            Business Summary
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Fast overview snapshot.
          </p>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        {summaryRows.map((row, i) => {
          const Icon = row.icon;
          return (
            <div
              key={i}
              className="flex items-center justify-between p-2.5 rounded-xl bg-[#141C2B] border border-slate-800 transition-colors"
            >
              <div className="flex items-center gap-2.5">
                <div className="w-7 h-7 rounded-lg bg-[#111827] border border-slate-700 flex items-center justify-center text-slate-400 shadow-2xs">
                  <Icon className="w-3.5 h-3.5" />
                </div>
                <span className="text-xs font-semibold text-slate-300">
                  {row.label}
                </span>
              </div>
              <span className="text-xs font-bold text-white text-right">
                {row.value}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}