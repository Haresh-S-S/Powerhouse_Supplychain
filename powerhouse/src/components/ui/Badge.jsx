import React from 'react';

export default function Badge({
  children,
  variant = 'default',
  size = 'sm',
  withDot = false,
  className = '',
}) {
  const variants = {
    Completed: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    Approved: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    Verified: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    Active: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    'Active Business': 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    success: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    High: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
    Rejected: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
    Critical: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
    Overdue: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
    danger: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
    'In Progress': 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    'Expiring Soon': 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    Pending: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
    Upcoming: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    warning: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    'Under Review': 'bg-indigo-500/15 text-indigo-400 border-indigo-500/30',
    Submitted: 'bg-sky-500/15 text-sky-400 border-sky-500/30',
    primary: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
    info: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
    'Not Required': 'bg-slate-800/80 text-slate-400 border-slate-700/60',
    Information: 'bg-slate-800/80 text-slate-400 border-slate-700/60',
    default: 'bg-slate-800/80 text-slate-400 border-slate-700/60',
  };

  const dotColors = {
    Completed: 'bg-emerald-500',
    Approved: 'bg-emerald-500',
    Verified: 'bg-emerald-500',
    Active: 'bg-emerald-500',
    High: 'bg-rose-500',
    Rejected: 'bg-rose-500',
    Critical: 'bg-rose-500',
    'In Progress': 'bg-blue-500',
    'Under Review': 'bg-indigo-500',
    Submitted: 'bg-sky-500',
    Pending: 'bg-amber-500',
    Upcoming: 'bg-amber-500',
    Information: 'bg-slate-400',
    default: 'bg-slate-400',
  };

  const sizes = {
    xs: 'px-2 py-0.5 text-[10px]',
    sm: 'px-2.5 py-0.5 text-xs',
    md: 'px-3 py-1 text-xs sm:text-sm',
  };

  const currentVariant = variants[variant] || variants.default;
  const currentDotColor = dotColors[variant] || dotColors.default;

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-semibold rounded-full border ${currentVariant} ${sizes[size] || sizes.sm} ${className}`}
    >
      {withDot && (
        <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${currentDotColor}`} />
      )}
      <span>{children}</span>
    </span>
  );
}
