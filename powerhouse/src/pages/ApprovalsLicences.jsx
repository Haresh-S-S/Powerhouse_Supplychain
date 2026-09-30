import React, { useState } from 'react';
import {
  FileCheck,
  CheckCircle2,
  Clock,
  AlertCircle,
  FileText,
  Building,
  ArrowRight,
  Milestone,
  HelpCircle
} from 'lucide-react';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import SearchInput from '../components/ui/SearchInput';
import EmptyState from '../components/ui/EmptyState';
import { useBusinessAnalysis } from '../context/BusinessAnalysisContext';

export default function ApprovalsLicences({ onNavigateToRoadmap, setModalState, showToast }) {
  const { businessTemplateBundle } = useBusinessAnalysis();
  const { approvalsStats, approvalsList } = businessTemplateBundle;

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [sortBy, setSortBy] = useState('name');

  const categories = ['All', ...new Set(approvalsList.map((a) => a.category))];
  const statuses = ['All', 'Completed', 'In Progress', 'Pending', 'Active'];

  const filteredApprovals = approvalsList
    .filter((item) => {
      const matchSearch = item.name.toLowerCase().includes(search.toLowerCase()) ||
        item.authority.toLowerCase().includes(search.toLowerCase()) ||
        item.category.toLowerCase().includes(search.toLowerCase());
      const matchStatus = statusFilter === 'All' || item.status === statusFilter ||
        (statusFilter === 'Completed' && item.status === 'Active');
      const matchCat = categoryFilter === 'All' || item.category === categoryFilter;
      return matchSearch && matchStatus && matchCat;
    })
    .sort((a, b) => {
      if (sortBy === 'name') return a.name.localeCompare(b.name);
      if (sortBy === 'progress') return (b.progress || 0) - (a.progress || 0);
      if (sortBy === 'priority') return a.priority === 'High' ? -1 : 1;
      return 0;
    });

  const handleOpenDetails = (approval) => {
    setModalState({
      isOpen: true,
      title: approval.name,
      type: 'approval-detail',
      data: approval,
    });
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-1">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Licences &amp; Approvals
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
            Manage all approvals, licences, and statutory mandates applicable to your business.
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          onClick={() => {
            onNavigateToRoadmap();
            showToast('Navigated to Approval Roadmap.');
          }}
          className="self-start sm:self-auto text-xs font-semibold"
        >
          <Milestone className="w-3.5 h-3.5" />
          <span>View Approval Roadmap</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Button>
      </div>

      {/* Top 4 Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5 sm:gap-5">
        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-400">Total Licences</div>
            <div className="text-xl sm:text-2xl font-black text-white mt-1">{approvalsStats.total}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Statutory mapped</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-950/80 text-blue-400 flex items-center justify-center border border-blue-800/80 shrink-0">
            <FileCheck className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-400">Completed / Active</div>
            <div className="text-xl sm:text-2xl font-black text-emerald-400 mt-1">{approvalsStats.completed || 6}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Licences active</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-950/80 text-emerald-400 flex items-center justify-center border border-emerald-800/80 shrink-0">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-400">In Progress / Renewal</div>
            <div className="text-xl sm:text-2xl font-black text-amber-400 mt-1">{approvalsStats.inProgress || 1}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Under audit / renewal</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-amber-950/80 text-amber-400 flex items-center justify-center border border-amber-800/80 shrink-0">
            <Clock className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-400">Pending / Required</div>
            <div className="text-xl sm:text-2xl font-black text-rose-400 mt-1">{approvalsStats.pending || 1}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Application queue</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-rose-950/80 text-rose-400 flex items-center justify-center border border-rose-800/80 shrink-0">
            <AlertCircle className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div className="flex-1 max-w-sm">
          <SearchInput
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onClear={() => setSearch('')}
            placeholder="Search licences, authorities..."
          />
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 text-xs font-medium rounded-xl border border-[#1E293B] bg-[#141C2B] hover:border-slate-700 focus:border-blue-500 focus:outline-none transition-all text-slate-200"
          >
            {statuses.map((st) => (
              <option key={st} value={st}>
                Status: {st}
              </option>
            ))}
          </select>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3 py-2 text-xs font-medium rounded-xl border border-[#1E293B] bg-[#141C2B] hover:border-slate-700 focus:border-blue-500 focus:outline-none transition-all text-slate-200"
          >
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                Category: {cat}
              </option>
            ))}
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 text-xs font-medium rounded-xl border border-[#1E293B] bg-[#141C2B] hover:border-slate-700 focus:border-blue-500 focus:outline-none transition-all text-slate-200"
          >
            <option value="name">Sort by Name</option>
            <option value="progress">Sort by Progress</option>
            <option value="priority">Sort by Priority</option>
          </select>
        </div>
      </div>

      {/* Approvals Grid */}
      {filteredApprovals.length === 0 ? (
        <EmptyState
          title="No approvals match your filter"
          description="Try resetting your search query or selecting 'All' for status and category filters."
          actionLabel="Clear Filters"
          onAction={() => {
            setSearch('');
            setStatusFilter('All');
            setCategoryFilter('All');
          }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
          {filteredApprovals.map((approval) => (
            <div
              key={approval.id}
              className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs hover:border-slate-700 transition-all duration-200 p-5 flex flex-col justify-between group"
            >
              <div>
                {/* Card Header */}
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-[10px] font-bold text-slate-300 bg-[#141C2B] px-2 py-0.5 rounded border border-slate-700">
                      {approval.category}
                    </span>
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue-950/80 text-blue-400 border border-blue-800/80">
                      VERIFIED SOURCE
                    </span>
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                        approval.priority === 'High'
                          ? 'bg-rose-950/80 text-rose-400 border border-rose-800/80'
                          : 'bg-slate-800 text-slate-300'
                      }`}
                    >
                      {approval.priority} Priority
                    </span>
                  </div>
                  <Badge variant={approval.status} withDot size="xs">
                    {approval.status}
                  </Badge>
                </div>

                <h3 className="text-sm font-bold text-white group-hover:text-blue-400 transition-colors mt-3">
                  {approval.name}
                </h3>

                <div className="flex items-center gap-1.5 text-xs text-slate-400 mt-1">
                  <Building className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                  <span className="truncate">{approval.authority}</span>
                </div>

                <p className="text-xs text-slate-400 mt-2.5 line-clamp-2 leading-relaxed">
                  {approval.description}
                </p>

                {/* Progress Bar */}
                <div className="mt-4 pt-3 border-t border-slate-800 space-y-1.5">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="font-semibold text-slate-400">Application Progress</span>
                    <span className="font-bold text-white">{approval.progress || 100}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        approval.status === 'Completed' || approval.status === 'Active'
                          ? 'bg-emerald-500'
                          : approval.status === 'In Progress' || approval.status === 'Expiring Soon'
                          ? 'bg-amber-500'
                          : 'bg-blue-500'
                      }`}
                      style={{ width: `${approval.progress || 100}%` }}
                    />
                  </div>
                </div>

                {/* Meta details */}
                <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400">
                  <div className="flex items-center gap-1">
                    <FileText className="w-3 h-3" />
                    <span>{approval.documentsCount || 3} Documents</span>
                  </div>
                  <span className="font-medium text-slate-300">{approval.dueDate || approval.expiryDate}</span>
                </div>
              </div>

              {/* Action Buttons: Why Required? & View Details */}
              <div className="pt-4 mt-4 border-t border-slate-800 flex items-center justify-between gap-2">
                <button
                  onClick={() => setModalState({
                    isOpen: true,
                    type: 'why-requirement',
                    data: { approval }
                  })}
                  className="px-2.5 py-1 rounded-lg bg-blue-950/70 hover:bg-blue-900 border border-blue-800/80 text-blue-400 hover:text-white font-semibold text-xs transition-colors cursor-pointer flex items-center gap-1 shadow-xs"
                  title="Inspect statutory justification, Act citations, and 8-step decision trace"
                >
                  <HelpCircle className="w-3.5 h-3.5" />
                  <span>Why is this required?</span>
                </button>

                <button
                  onClick={() => handleOpenDetails(approval)}
                  className="text-xs font-semibold text-slate-300 hover:text-white flex items-center gap-1 cursor-pointer transition-colors"
                >
                  <span>View Details</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}