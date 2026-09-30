import React from 'react';

export default function ProfileField({
  label,
  value,
  isEditing = false,
  name,
  type = 'text',
  options = [],
  onChange,
  icon: Icon,
  badge = null,
  placeholder = '',
  className = '',
}) {
  return (
    <div className={`flex flex-col sm:flex-row sm:items-center justify-between py-3 border-b border-slate-800/80 last:border-b-0 gap-2 ${className}`}>
      <div className="flex items-center gap-2 min-w-[180px] shrink-0">
        {Icon && <Icon className="w-4 h-4 text-slate-400 shrink-0" />}
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
          {label}
        </span>
      </div>

      <div className="flex-1 sm:text-right min-w-0">
        {isEditing ? (
          type === 'select' ? (
            <select
              name={name}
              value={value || ''}
              onChange={onChange}
              className="w-full sm:w-auto min-w-[220px] px-3 py-1.5 text-xs font-medium rounded-xl border border-slate-700 bg-[#141C2B] hover:border-slate-600 focus:border-blue-500 focus:outline-none transition-all cursor-pointer text-slate-100"
            >
              {options.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          ) : type === 'textarea' ? (
            <textarea
              name={name}
              value={value || ''}
              onChange={onChange}
              placeholder={placeholder}
              rows={2}
              className="w-full px-3 py-1.5 text-xs font-medium rounded-xl border border-slate-700 bg-[#141C2B] hover:border-slate-600 focus:border-blue-500 focus:outline-none transition-all text-slate-100"
            />
          ) : (
            <input
              type={type}
              name={name}
              value={value || ''}
              onChange={onChange}
              placeholder={placeholder}
              className="w-full sm:w-auto min-w-[220px] px-3 py-1.5 text-xs font-medium rounded-xl border border-slate-700 bg-[#141C2B] hover:border-slate-600 focus:border-blue-500 focus:outline-none transition-all text-slate-100 text-left sm:text-right"
            />
          )
        ) : badge ? (
          <div className="flex sm:justify-end">{badge}</div>
        ) : (
          <span className="text-xs font-bold text-white truncate block">
            {value || <span className="text-slate-500 font-normal italic">Not provided</span>}
          </span>
        )}
      </div>
    </div>
  );
}