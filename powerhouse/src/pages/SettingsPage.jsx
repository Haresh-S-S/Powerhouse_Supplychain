import React, { useState } from 'react';
import {
  Building,
  Bell,
  Sliders,
  ShieldAlert,
  Pencil,
  Download,
  Trash2,
  Repeat
} from 'lucide-react';
import Button from '../components/ui/Button';
import { initialSettings } from '../data/settingsData';
import { useBusinessAnalysis } from '../context/BusinessAnalysisContext';

export default function SettingsPage({ onNavigateToProfile, showToast, setModalState }) {
  const [settings, setSettings] = useState(initialSettings);
  const { analysisResult, businessCategoryLabel, resetOnboarding } = useBusinessAnalysis();

  const businessSummary = analysisResult?.businessSummary || {};
  const businessOverview = {
    name: businessSummary.businessName || 'Tiruppur Textile Works',
    industry: businessCategoryLabel || 'Clothing & Textile Retail',
    location: businessSummary.city
      ? `${businessSummary.city}${businessSummary.state ? `, ${businessSummary.state}` : ''}`
      : 'Tiruppur, Tamil Nadu',
    size: businessSummary.companySize
      ? `${businessSummary.companySize} (${businessSummary.employees ?? '25'} Employees)`
      : 'Small Enterprise (25 Employees)',
  };

  const handleSwitchBusinessType = () => {
    setModalState({
      isOpen: true,
      title: 'Switch Business Type',
      type: 'switch-business',
      data: {
        message: 'This will take you back to the business description screen so you can re-classify your business. Your current dashboard data will be replaced with the new category.',
      },
    });
  };

  const handleToggleNotification = (key) => {
    setSettings((prev) => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [key]: !prev.notifications[key],
      },
    }));
    showToast('Notification preference updated.');
  };

  const handleDensityChange = (density) => {
    setSettings((prev) => ({
      ...prev,
      display: { ...prev.display, density },
    }));
    showToast(`Display density set to ${density}.`);
  };

  const handleOpenDeleteConfirm = () => {
    setModalState({
      isOpen: true,
      title: 'Delete Business Data Confirmation',
      type: 'delete-confirm',
      data: {
        message: `This will purge local prototype data for ${businessOverview.name}. This action cannot be reversed.`,
      },
    });
  };

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Top Header */}
      <div className="pb-1">
        <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
          Settings
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
          Manage your POWER HOUSE platform configuration and compliance parameters.
        </p>
      </div>

      {/* Section 1: Business Settings */}
      <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-5 sm:p-6">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-blue-950 text-blue-400 border border-blue-800">
              <Building className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white leading-none">
                Business Settings
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Primary organization configuration
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={handleSwitchBusinessType}
              className="text-xs font-semibold text-slate-200"
            >
              <Repeat className="w-3.5 h-3.5" />
              <span>Switch Business Type</span>
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={onNavigateToProfile}
              className="text-xs font-semibold text-blue-400 hover:text-blue-300"
            >
              <Pencil className="w-3.5 h-3.5" />
              <span>Edit Business Profile</span>
            </Button>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-3.5 bg-[#141C2B] rounded-xl border border-slate-800">
            <span className="text-slate-400 font-medium block">Business Name</span>
            <span className="font-bold text-white text-sm mt-0.5 block">{businessOverview.name}</span>
          </div>
          <div className="p-3.5 bg-[#141C2B] rounded-xl border border-slate-800">
            <span className="text-slate-400 font-medium block">Business Category</span>
            <span className="font-bold text-white text-sm mt-0.5 block">{businessOverview.industry}</span>
          </div>
          <div className="p-3.5 bg-[#141C2B] rounded-xl border border-slate-800">
            <span className="text-slate-400 font-medium block">Business Location</span>
            <span className="font-bold text-white text-sm mt-0.5 block">{businessOverview.location}</span>
          </div>
          <div className="p-3.5 bg-[#141C2B] rounded-xl border border-slate-800">
            <span className="text-slate-400 font-medium block">Business Size</span>
            <span className="font-bold text-white text-sm mt-0.5 block">{businessOverview.size}</span>
          </div>
        </div>
      </div>

      {/* Section 2: Notification Preferences */}
      <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-5 sm:p-6">
        <div className="flex items-center gap-2.5 pb-4 border-b border-slate-800">
          <div className="p-1.5 rounded-lg bg-blue-950 text-blue-400 border border-blue-800">
            <Bell className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white leading-none">
              Notification Preferences
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Select channels and frequency of compliance reminders
            </p>
          </div>
        </div>

        <div className="mt-4 divide-y divide-slate-800 text-xs">
          {[
            { key: 'emailNotifications', label: 'Email Notifications', desc: 'Receive statutory audit digests and critical regulatory updates via email.' },
            { key: 'deadlineReminders', label: 'Deadline Reminders', desc: 'Alerts 7 days and 48 hours prior to compliance and filing deadlines.' },
            { key: 'documentExpiryAlerts', label: 'Document Expiry Alerts', desc: 'Notifications when licenses or NOC certificates near their expiration date.' },
            { key: 'schemeUpdates', label: 'Government Scheme Updates', desc: 'AI matching recommendations for newly announced central and state MSME subsidies.' },
          ].map((item) => {
            const isChecked = settings.notifications[item.key];

            return (
              <div key={item.key} className="py-3.5 flex items-center justify-between gap-4">
                <div>
                  <h3 className="font-bold text-white">{item.label}</h3>
                  <p className="text-slate-400 mt-0.5">{item.desc}</p>
                </div>

                <button
                  type="button"
                  onClick={() => handleToggleNotification(item.key)}
                  className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors cursor-pointer shrink-0 ${
                    isChecked ? 'bg-blue-600' : 'bg-slate-700'
                  }`}
                  role="switch"
                  aria-checked={isChecked}
                  aria-label={item.label}
                >
                  <div
                    className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform ${
                      isChecked ? 'translate-x-5' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Section 3: Display Preferences */}
      <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-5 sm:p-6">
        <div className="flex items-center gap-2.5 pb-4 border-b border-slate-800">
          <div className="p-1.5 rounded-lg bg-blue-950 text-blue-400 border border-blue-800">
            <Sliders className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white leading-none">
              Display Preferences
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Customize dashboard layout and interface density
            </p>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-4 bg-[#141C2B] rounded-xl border border-slate-800 space-y-2">
            <span className="font-bold text-white block">Dashboard Density</span>
            <div className="flex items-center gap-2 pt-1">
              {['Comfortable', 'Compact'].map((d) => (
                <button
                  key={d}
                  onClick={() => handleDensityChange(d)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold cursor-pointer transition-all ${
                    settings.display.density === d
                      ? 'bg-blue-600 text-white shadow-2xs'
                      : 'bg-[#111827] text-slate-300 border border-slate-700'
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          <div className="p-4 bg-[#141C2B] rounded-xl border border-slate-800 space-y-2">
            <span className="font-bold text-white block">Sidebar Navigation</span>
            <div className="flex items-center gap-2 pt-1">
              {['Expanded', 'Collapsed'].map((s) => (
                <button
                  key={s}
                  onClick={() => {
                    setSettings((prev) => ({ ...prev, display: { ...prev.display, sidebar: s } }));
                    showToast(`Sidebar mode set to ${s}.`);
                  }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold cursor-pointer transition-all ${
                    settings.display.sidebar === s
                      ? 'bg-blue-600 text-white shadow-2xs'
                      : 'bg-[#111827] text-slate-300 border border-slate-700'
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Section 4: Data & Privacy */}
      <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-5 sm:p-6">
        <div className="flex items-center gap-2.5 pb-4 border-b border-slate-800">
          <div className="p-1.5 rounded-lg bg-blue-950 text-blue-400 border border-blue-800">
            <ShieldAlert className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white leading-none">
              Data &amp; Privacy
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Local enterprise isolation and data portability
            </p>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-3">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => showToast('Enterprise data sandbox settings verified.')}
            className="text-xs font-semibold"
          >
            <span>Manage Business Data</span>
          </Button>

          <Button
            variant="secondary"
            size="sm"
            onClick={() => showToast('Exporting business compliance vault JSON...')}
            className="text-xs font-semibold text-slate-200"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Business Data</span>
          </Button>

          <Button
            variant="secondary"
            size="sm"
            onClick={handleOpenDeleteConfirm}
            className="text-xs font-semibold text-rose-400 hover:bg-rose-950/40 hover:border-rose-800 ml-auto"
          >
            <Trash2 className="w-3.5 h-3.5 text-rose-400" />
            <span>Delete Business Data</span>
          </Button>
        </div>
      </div>

      {/* Section 5: About POWER HOUSE */}
      <div className="bg-[#111827] rounded-2xl p-5 sm:p-6 text-white border border-[#1E293B] shadow-md">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center font-black text-white text-sm">
            PH
          </div>
          <div>
            <h3 className="font-bold text-base text-white">{settings.about.platform}</h3>
            <span className="text-xs text-slate-400">Compliance. Simplified.</span>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-3 border-t border-slate-800 text-slate-300">
          <div>
            <span className="text-slate-400 block text-[11px]">Version</span>
            <span className="font-semibold">{settings.about.version}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[11px]">Build</span>
            <span className="font-semibold">{settings.about.build}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[11px]">Engine</span>
            <span className="font-semibold text-blue-400">Deterministic Engine v2.4</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[11px]">Environment</span>
            <span className="font-semibold text-emerald-400">Operational</span>
          </div>
        </div>
      </div>
    </div>
  );
}