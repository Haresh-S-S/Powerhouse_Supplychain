import React, { useState } from 'react';
import {
  LayoutDashboard,
  FileText,
  CalendarCheck,
  FolderLock,
  Send,
  Landmark,
  Bell,
  BarChart3,
  Brain,
  Settings,
  Leaf,
  Truck,
  Users,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  MapPin,
  X,
  Building,
} from 'lucide-react';
import { navItems } from '../../data/mockData';
import { useBusinessAnalysis } from '../../context/BusinessAnalysisContext';
import { useAuth } from '../../context/AuthContext';

const iconMap = {
  LayoutDashboard,
  FileText,
  CalendarCheck,
  Truck,
  Users,
  FolderLock,
  Send,
  Landmark,
  Bell,
  BarChart3,
  Brain,
  Settings,
  Leaf,
};

export default function Sidebar({
  activeNav,
  setActiveNav,
  mobileOpen,
  setMobileOpen,
  _onContactSupport,
  onSwitchBusiness,
  isCollapsed = false,
  onToggleCollapse,
}) {
  const auth = useAuth();
  const { businessTemplateBundle, analysisResult, resetOnboarding } = useBusinessAnalysis();
  const [tooltip, setTooltip] = useState(null);

  const userName = auth?.user?.fullName || 'Business Owner';
  const userInitials = auth?.user?.fullName
    ? auth.user.fullName
        .trim()
        .split(/\s+/)
        .map((n) => n[0])
        .slice(0, 2)
        .join('')
        .toUpperCase()
    : 'BO';

  const businessName = analysisResult?.businessSummary?.businessName || 'Tiruppur Textile Works';
  const categoryLabel = businessTemplateBundle?.meta?.categoryLabel || 'Clothing & Textile Retail';
  const city = analysisResult?.businessSummary?.city || 'Tiruppur';
  const state = analysisResult?.businessSummary?.state || 'Tamil Nadu';
  const locationString = `${city}, ${state}`;

  const unreadAlertsCount = (businessTemplateBundle?.alertsList || []).filter((a) => !a.read).length;

  const resolvedNavItems = navItems.map((item) =>
    item.id === 'alerts'
      ? { ...item, badge: unreadAlertsCount > 0 ? String(unreadAlertsCount) : '3' }
      : item
  );

  const handleSwitch = () => {
    if (onSwitchBusiness) {
      onSwitchBusiness();
    } else {
      resetOnboarding();
    }
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div
          onClick={() => setMobileOpen(false)}
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-xs lg:hidden transition-opacity"
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 lg:static lg:z-auto h-full h-[100dvh] shrink-0 bg-[#0B0F17] text-slate-300 flex flex-col border-r border-[#1E293B] transition-all duration-200 ease-in-out select-none ${
          mobileOpen ? 'translate-x-0 w-[250px]' : '-translate-x-full lg:translate-x-0'
        } ${isCollapsed ? 'lg:w-[64px]' : 'lg:w-[var(--sidebar-width,250px)]'}`}
      >
        {/* 1. TOP: Brand Header (Never scrolls, 52px) */}
        {isCollapsed ? (
          <div className="h-13 min-h-[52px] relative flex items-center justify-between border-b border-[#1E293B] px-2 shrink-0">
            <div className="w-8 h-8 rounded-lg overflow-hidden bg-black border border-amber-500/30 flex items-center justify-center p-0.5 shrink-0" title="POWER HOUSE">
              <img src="/logo.png" alt="POWER HOUSE" className="w-full h-full object-contain" />
            </div>
            <button
              onClick={onToggleCollapse}
              className="hidden lg:flex w-6 h-6 items-center justify-center rounded text-slate-400 hover:text-white hover:bg-[#141C2B] border border-slate-700/60 transition-colors cursor-pointer"
              title="Expand sidebar"
              aria-label="Expand sidebar"
            >
              <ChevronRight className="w-3.5 h-3.5 text-blue-400" />
            </button>
          </div>
        ) : (
          <div className="h-13 min-h-[52px] relative flex items-center justify-between border-b border-[#1E293B] px-3.5 shrink-0">
            <div className="flex items-center gap-2.5 min-w-0 pr-6">
              <div className="w-8 h-8 rounded-lg overflow-hidden bg-black border border-amber-500/30 flex items-center justify-center shadow-sm shadow-amber-500/10 shrink-0 p-0.5">
                <img src="/logo.png" alt="POWER HOUSE" className="w-full h-full object-contain" />
              </div>
              <div className="min-w-0">
                <div className="text-white font-bold text-xs tracking-wide leading-none uppercase truncate">
                  POWER HOUSE
                </div>
                <div className="text-[10px] font-medium text-slate-400 mt-1 tracking-normal truncate">
                  Compliance. Simplified.
                </div>
              </div>
            </div>

            <div className="flex items-center">
              <button
                onClick={onToggleCollapse}
                className="hidden lg:flex absolute right-2.5 top-1/2 -translate-y-1/2 w-6 h-6 items-center justify-center rounded text-slate-400 hover:text-white hover:bg-[#141C2B] border border-slate-700/60 transition-colors cursor-pointer"
                title="Collapse sidebar"
                aria-label="Collapse sidebar"
              >
                <ChevronLeft className="w-3.5 h-3.5 text-slate-300" />
              </button>
              <button
                onClick={() => setMobileOpen(false)}
                className="p-1 text-slate-400 hover:text-white rounded lg:hidden cursor-pointer"
                aria-label="Close Sidebar"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* 2. MIDDLE: Navigation Section */}
        <div className={`flex-1 min-h-0 overflow-y-auto ${isCollapsed ? 'px-1.5 py-2 space-y-1' : 'px-2 py-2 space-y-1'} sidebar-scroll`}>
          {resolvedNavItems.map((item) => {
            const Icon = iconMap[item.icon] || LayoutDashboard;
            const isActive =
              activeNav === item.id ||
              (activeNav === 'dashboard' && item.id === 'overview') ||
              (activeNav === 'overview' && item.id === 'overview');

            return (
              <button
                key={item.id}
                onClick={() => {
                  setActiveNav(item.id === 'overview' ? 'dashboard' : item.id);
                  if (mobileOpen) setMobileOpen(false);
                }}
                onMouseEnter={(e) => {
                  if (isCollapsed) {
                    const rect = e.currentTarget.getBoundingClientRect();
                    setTooltip({
                      label: item.label,
                      badge: item.badge,
                      top: rect.top + rect.height / 2,
                    });
                  }
                }}
                onMouseLeave={() => setTooltip(null)}
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center h-9 px-0' : 'justify-between px-3 h-9'
                } rounded-lg text-xs font-medium transition-all duration-150 group cursor-pointer relative ${
                  isActive
                    ? 'bg-blue-600 text-white font-semibold shadow-xs shadow-blue-500/20'
                    : 'text-slate-300 hover:text-white hover:bg-[#141C2B]'
                }`}
                title={isCollapsed ? undefined : item.label}
                aria-label={item.label}
              >
                <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'gap-2.5 min-w-0'}`}>
                  <Icon
                    className={`w-4 h-4 shrink-0 transition-colors ${
                      isActive ? 'text-white' : 'text-slate-400 group-hover:text-slate-200'
                    }`}
                  />
                  {!isCollapsed && <span className="truncate">{item.label}</span>}
                </div>

                {!isCollapsed && item.badge && (
                  <span
                    className={`px-1.5 py-0.2 text-[10px] rounded-full font-bold ${
                      isActive
                        ? 'bg-white text-blue-700'
                        : 'bg-rose-950/80 text-rose-400 border border-rose-800/80'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}

                {isCollapsed && item.badge && (
                  <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-500 ring-2 ring-[#0B0F17]" />
                )}
              </button>
            );
          })}
        </div>

        {/* 3. BOTTOM (PINNED): Business Context Card + User Card */}
        <div className="shrink-0 p-3 border-t border-[#1E293B] bg-[#0B0F17] space-y-2">
          {!isCollapsed ? (
            <>
              <div className="px-1 text-[10px] font-bold tracking-wider text-slate-400 uppercase">
                BUSINESS CONTEXT
              </div>
              <div className="bg-[#141C2B] border border-[#1E293B] rounded-xl p-2.5 space-y-1">
                <div className="flex items-center justify-between gap-1.5">
                  <span className="font-bold text-white text-xs truncate" title={businessName}>
                    {businessName}
                  </span>
                  <span className="px-1.5 py-0.2 rounded-full text-[9px] font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 shrink-0">
                    Active
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 leading-tight truncate" title={categoryLabel}>
                  {categoryLabel}
                </p>
                <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
                  <MapPin className="w-3 h-3 text-slate-400 shrink-0" />
                  <span className="truncate" title={locationString}>{locationString}</span>
                </div>
                <button
                  onClick={handleSwitch}
                  className="w-full mt-1.5 py-1 px-2.5 rounded-lg bg-[#111827] hover:bg-[#1E293B] text-slate-300 hover:text-white text-xs font-medium border border-slate-700/80 transition-colors text-center cursor-pointer"
                >
                  Switch Business
                </button>
              </div>

              {/* User Profile Capsule */}
              <div className="p-2 rounded-xl bg-[#111827] border border-[#1E293B] flex items-center justify-between">
                <div className="flex items-center gap-2 min-w-0">
                  <div className="w-7 h-7 rounded-full bg-blue-600 text-white font-bold text-xs flex items-center justify-center shrink-0">
                    {userInitials}
                  </div>
                  <div className="min-w-0">
                    <div className="text-xs font-semibold text-white leading-none truncate" title={userName}>
                      {userName}
                    </div>
                    <div className="text-[10px] text-slate-400 mt-1 leading-none truncate">
                      Business Owner
                    </div>
                  </div>
                </div>
                <ChevronDown className="w-3 h-3 text-slate-400 shrink-0" />
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center gap-1.5 py-1">
              <button
                onClick={handleSwitch}
                onMouseEnter={(e) => {
                  const rect = e.currentTarget.getBoundingClientRect();
                  setTooltip({
                    label: `${businessName} (${categoryLabel}) • Click to switch`,
                    top: rect.top + rect.height / 2,
                  });
                }}
                onMouseLeave={() => setTooltip(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#141C2B] transition-colors cursor-pointer"
                aria-label="Switch Business"
              >
                <Building className="w-4 h-4 text-slate-400 hover:text-blue-400" />
              </button>
              <div
                onMouseEnter={(e) => {
                  const rect = e.currentTarget.getBoundingClientRect();
                  setTooltip({
                    label: `${userName} (Business Owner)`,
                    top: rect.top + rect.height / 2,
                  });
                }}
                onMouseLeave={() => setTooltip(null)}
                className="w-7 h-7 rounded-full bg-blue-600 text-white font-bold text-xs flex items-center justify-center shrink-0 cursor-pointer shadow-xs"
              >
                {userInitials}
              </div>
            </div>
          )}
        </div>
      </aside>

      {/* Floating Tooltip for Collapsed Sidebar */}
      {isCollapsed && tooltip && (
        <div
          style={{ top: `${tooltip.top}px` }}
          className="fixed left-[76px] -translate-y-1/2 px-2.5 py-1 bg-[#111827] text-white text-xs font-semibold rounded-lg shadow-2xl border border-[#1E293B] whitespace-nowrap z-50 pointer-events-none flex items-center gap-2 animate-in fade-in duration-100"
        >
          <span>{tooltip.label}</span>
          {tooltip.badge && (
            <span className="px-1.5 py-0.2 rounded-full text-[10px] font-bold bg-rose-950 text-rose-400 border border-rose-800">
              {tooltip.badge}
            </span>
          )}
        </div>
      )}
    </>
  );
}
