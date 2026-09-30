import React, { useState } from 'react';
import {
  BellRing,
  AlertTriangle,
  Clock,
  Info,
  CheckCheck,
  Calendar,
  ArrowRight
} from 'lucide-react';
import Button from '../components/ui/Button';
import SearchInput from '../components/ui/SearchInput';
import EmptyState from '../components/ui/EmptyState';
import { useBusinessAnalysis } from '../context/BusinessAnalysisContext';

export default function AlertsPage({ onNavigate, showToast, setModalState }) {
  const { businessTemplateBundle } = useBusinessAnalysis();
  const { alertsStats, alertsList: initialAlertsList } = businessTemplateBundle;

  const [alerts, setAlerts] = useState(initialAlertsList);
  const [activeTab, setActiveTab] = useState('All');
  const [search, setSearch] = useState('');

  const tabs = ['All', 'Critical', 'Upcoming', 'Information'];

  const handleMarkAsRead = (id) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, read: true } : a))
    );
    showToast('Alert marked as read.');
  };

  const handleMarkAllAsRead = () => {
    setAlerts((prev) => prev.map((a) => ({ ...a, read: true })));
    showToast('All alerts marked as read.');
  };

  const filteredAlerts = alerts.filter((alert) => {
    const matchSearch =
      alert.title.toLowerCase().includes(search.toLowerCase()) ||
      alert.description.toLowerCase().includes(search.toLowerCase()) ||
      alert.category.toLowerCase().includes(search.toLowerCase());

    const matchTab =
      activeTab === 'All' ||
      (activeTab === 'Critical' && alert.severity === 'critical') ||
      (activeTab === 'Upcoming' && alert.severity === 'upcoming') ||
      (activeTab === 'Information' && alert.severity === 'information');

    return matchSearch && matchTab;
  });

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-1">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Alerts &amp; Notifications
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
            Stay informed about statutory compliance deadlines, inspections, and regulatory notices.
          </p>
        </div>

        <Button
          variant="secondary"
          size="sm"
          onClick={handleMarkAllAsRead}
          className="self-start sm:self-auto text-xs font-semibold"
        >
          <CheckCheck className="w-3.5 h-3.5" />
          <span>Mark All as Read</span>
        </Button>
      </div>

      {/* Top 3 Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-rose-400 uppercase tracking-wider">Critical Alerts</div>
            <div className="text-2xl font-black text-white mt-1">{alertsStats.critical || 1}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Immediate action required</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-rose-950/80 text-rose-400 flex items-center justify-center border border-rose-800/80">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-amber-400 uppercase tracking-wider">Upcoming Deadlines</div>
            <div className="text-2xl font-black text-white mt-1">{alertsStats.upcoming || 2}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Due in next 14 days</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-amber-950/80 text-amber-400 flex items-center justify-center border border-amber-800/80">
            <Clock className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-blue-400 uppercase tracking-wider">Information</div>
            <div className="text-2xl font-black text-white mt-1">{alertsStats.information || 1}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Advisories &amp; scheme notices</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-950/80 text-blue-400 flex items-center justify-center border border-blue-800/80">
            <Info className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Search and Category Filter Tabs */}
      <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
                activeTab === tab
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'text-slate-400 hover:text-white hover:bg-[#141C2B]'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className="w-full md:max-w-xs">
          <SearchInput
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onClear={() => setSearch('')}
            placeholder="Search alerts..."
          />
        </div>
      </div>

      {/* Alerts List */}
      {filteredAlerts.length === 0 ? (
        <EmptyState
          title="No alerts in this category"
          description="Adjust your search or filter tabs to review historical compliance notices."
          actionLabel="View All Alerts"
          onAction={() => {
            setSearch('');
            setActiveTab('All');
          }}
        />
      ) : (
        <div className="space-y-3">
          {filteredAlerts.map((alert) => {
            const isCritical = alert.severity === 'critical';
            const isUpcoming = alert.severity === 'upcoming';

            return (
              <div
                key={alert.id}
                className={`bg-[#111827] rounded-2xl border transition-all p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
                  !alert.read
                    ? isCritical
                      ? 'border-rose-900/60 bg-rose-950/20'
                      : isUpcoming
                      ? 'border-amber-900/60 bg-amber-950/20'
                      : 'border-blue-900/60 bg-blue-950/20'
                    : 'border-slate-800/80 bg-[#111827] opacity-80'
                }`}
              >
                <div className="flex items-start gap-3.5 min-w-0 flex-1">
                  <div
                    className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${
                      isCritical
                        ? 'bg-rose-950 text-rose-400 border border-rose-800'
                        : isUpcoming
                        ? 'bg-amber-950 text-amber-400 border border-amber-800'
                        : 'bg-blue-950 text-blue-400 border border-blue-800'
                    }`}
                  >
                    {isCritical ? (
                      <AlertTriangle className="w-4 h-4" />
                    ) : isUpcoming ? (
                      <Clock className="w-4 h-4" />
                    ) : (
                      <Info className="w-4 h-4" />
                    )}
                  </div>

                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-sm font-bold text-white">{alert.title}</h3>
                      {!alert.read && (
                        <span className="w-2 h-2 rounded-full bg-blue-500" />
                      )}
                      <span className="text-[10px] font-bold text-slate-300 bg-[#141C2B] px-2 py-0.5 rounded border border-slate-700">
                        {alert.category}
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                      {alert.description}
                    </p>

                    <div className="flex items-center gap-1.5 text-[11px] text-slate-400 mt-2">
                      <Calendar className="w-3 h-3 text-slate-400" />
                      <span>{alert.date}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-end gap-2 shrink-0 pt-2 sm:pt-0 border-t sm:border-t-0 border-slate-800">
                  {!alert.read && (
                    <button
                      onClick={() => handleMarkAsRead(alert.id)}
                      className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-800 cursor-pointer"
                    >
                      Mark as read
                    </button>
                  )}

                  {alert.actionRoute && (
                    <button
                      onClick={() => onNavigate(alert.actionRoute)}
                      className="px-3 py-1.5 rounded-lg bg-blue-950 text-blue-400 hover:bg-blue-900 text-xs font-semibold transition-colors flex items-center gap-1 cursor-pointer border border-blue-800"
                    >
                      <span>Take Action</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}