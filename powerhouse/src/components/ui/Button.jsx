import React from 'react';

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  onClick,
  disabled = false,
  className = '',
  type = 'button',
  ...props
}) {
  const baseStyles =
    'inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-150 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed select-none focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-blue-500';

  const variants = {
    primary:
      'bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white shadow-sm shadow-blue-900/40 active:scale-[0.98]',
    secondary:
      'bg-slate-900/90 hover:bg-slate-800 active:bg-slate-700 text-slate-200 border border-slate-700/80 active:scale-[0.98]',
    outline:
      'bg-transparent hover:bg-slate-800/80 active:bg-slate-800 text-slate-300 border border-slate-700 active:scale-[0.98]',
    ghost:
      'bg-transparent hover:bg-slate-800 text-slate-400 hover:text-white active:bg-slate-700',
    danger:
      'bg-rose-500/15 hover:bg-rose-500/25 active:bg-rose-500/35 text-rose-400 border border-rose-500/30 active:scale-[0.98]',
  };

  const sizes = {
    xs: 'px-2.5 py-1 text-xs gap-1.5',
    sm: 'px-3.5 py-1.5 text-xs sm:text-sm gap-1.5',
    md: 'px-4 py-2 text-xs sm:text-sm gap-2',
    lg: 'px-5 py-2.5 text-sm sm:text-base gap-2.5',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${variants[variant] || variants.primary} ${sizes[size] || sizes.md} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
