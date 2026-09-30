import React from 'react';
import {
  ClipboardCheck,
  ListTodo,
  CalendarDays,
  Gauge,
  ChevronRight
} from 'lucide-react';

const iconComponents = {
  ClipboardCheck,
  ListTodo,
  CalendarDays,
  Gauge,
};

const accentStyles = {
  blue: {
    bg: 'bg-blue-50/80',
    border: 'border-blue-100',
    iconBg: 'bg-blue-600',
    text: 'text-blue-600',
    hoverBorder: 'hover:border-blue-300',
    glow: 'group-hover:shadow-blue-500/5',
  },
  orange: {
    bg: 'bg-amber-50/80',
    border: 'border-amber-100',
    iconBg: 'bg-amber-500',
    text: 'text-amber-600',
    hoverBorder: 'hover:border-amber-300',
    glow: 'group-hover:shadow-amber-500/5',
  },
  red: {
    bg: 'bg-rose-50/80',
    border: 'border-rose-100',
    iconBg: 'bg-rose-500',
    text: 'text-rose-600',
    hoverBorder: 'hover:border-rose-300',
    glow: 'group-hover:shadow-rose-500/5',
  },
  green: {
    bg: 'bg-emerald-50/80',
    border: 'border-emerald-100',
    iconBg: 'bg-emerald-500',
    text: 'text-emerald-600',
    hoverBorder: 'hover:border-emerald-300',
    glow: 'group-hover:shadow-emerald-500/5',
  },
};

export default function StatCard({ item, onClick }) {
  const Icon = iconComponents[item.icon] || ClipboardCheck;
  const accent = accentStyles[item.accent] || accentStyles.blue;

  return (
    <div
      onClick={onClick}
      className={`group relative bg-white p-5 rounded-2xl border border-slate-200/90 shadow-2xs hover:shadow-md transition-all duration-200 cursor-pointer flex flex-col justify-between ${accent.hoverBorder}`}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
            {item.title}
          </span>
          <div className="mt-2 text-3xl font-extrabold text-slate-900 tracking-tight">
            {item.value}
          </div>
        </div>

        <div
          className={`w-11 h-11 rounded-xl flex items-center justify-center text-white shadow-xs ${accent.iconBg} transition-transform duration-200 group-hover:scale-105`}
        >
          <Icon className="w-5 h-5 stroke-[2.2]" />
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
        <div className="flex items-center gap-1 font-semibold text-slate-600 group-hover:text-blue-600 transition-colors">
          <span>{item.subtitle}</span>
          <ChevronRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-0.5 transition-all" />
        </div>

        {item.trend && (
          <span className="text-[11px] font-medium text-slate-400">
            {item.trend}
          </span>
        )}
      </div>
    </div>
  );
}
