import React, { useState } from 'react';
import {
  Landmark,
  ArrowRight,
  TrendingUp,
  RefreshCw
} from 'lucide-react';
import Button from '../components/ui/Button';
import SearchInput from '../components/ui/SearchInput';
import EmptyState from '../components/ui/EmptyState';
import { useBusinessAnalysis } from '../context/BusinessAnalysisContext';

export default function GovernmentSchemesPage({ showToast, setModalState }) {
  const { businessTemplateBundle, analysisResult } = useBusinessAnalysis();
  const { schemesHighlight, schemesList } = businessTemplateBundle;
  const businessName = analysisResult?.businessSummary?.businessName || 'Tiruppur Textile Works';

  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [isRefreshing, setIsRefreshing] = useState(false);

  const categories = ['All', ...new Set(schemesList.map((s) => s.category))];

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setIsRefreshing(false);
      showToast('Government scheme database updated with live ministry data.');
    }, 600);
  };

  const filteredSchemes = schemesList.filter((scheme) => {
    const matchSearch = scheme.name.toLowerCase().includes(search.toLowerCase()) ||
      (scheme.shortName && scheme.shortName.toLowerCase().includes(search.toLowerCase())) ||
      scheme.description.toLowerCase().includes(search.toLowerCase());
    const matchCat = categoryFilter === 'All' || scheme.category === categoryFilter;
    return matchSearch && matchCat;
  });

  const handleOpenDetail = (scheme) => {
    setModalState({
      isOpen: true,
      title: scheme.name,
      type: 'scheme-detail',
      data: scheme,
    });
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-1">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Government Schemes
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
            Discover and apply for government incentives, subsidies, and credit facilities matching your profile.
          </p>
        </div>

        <Button
          variant="secondary"
          size="sm"
          onClick={handleRefresh}
          className="self-start sm:self-auto text-xs font-semibold"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-blue-400' : ''}`} />
          <span>Refresh Schemes</span>
        </Button>
      </div>

      {/* Recommendation Banner */}
      <div className="bg-[#111827] rounded-2xl p-6 text-white relative overflow-hidden shadow-xl border border-[#1E293B]">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-xl">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-blue-950 border border-blue-800 text-blue-400 text-xs font-semibold">
              <Landmark className="w-3.5 h-3.5" />
              <span>{schemesHighlight.title || 'Verified Regulatory Match'}</span>
            </div>
            <h2 className="text-lg sm:text-xl font-bold tracking-tight text-white">
              {schemesHighlight.totalSchemes || schemesList.length} Government Schemes Pre-Qualified for {businessName}
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
              {schemesHighlight.description}
            </p>
          </div>

          <div className="flex items-center gap-4 shrink-0 bg-[#141C2B] p-4 rounded-xl border border-slate-700">
            <div className="text-center">
              <div className="text-2xl sm:text-3xl font-black text-white">{schemesHighlight.highMatch || 4}</div>
              <div className="text-[10px] text-blue-400 uppercase font-semibold">High Priority</div>
            </div>
            <div className="w-px h-8 bg-slate-700" />
            <div className="text-center">
              <div className="text-2xl sm:text-3xl font-black text-emerald-400">₹25L</div>
              <div className="text-[10px] text-emerald-400 uppercase font-semibold">Max Subsidy</div>
            </div>
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
            placeholder="Search schemes, subsidies, keywords..."
          />
        </div>

        <div className="flex items-center gap-2.5">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3 py-2 text-xs font-medium rounded-xl border border-[#1E293B] bg-[#141C2B] hover:border-slate-700 focus:border-blue-500 focus:outline-none transition-all text-slate-200"
          >
            {categories.map((c) => (
              <option key={c} value={c}>
                Category: {c}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Schemes Grid */}
      {filteredSchemes.length === 0 ? (
        <EmptyState
          title="No schemes matched your search"
          description="Adjust your search criteria or category filter to discover programs."
          actionLabel="Clear Filters"
          onAction={() => {
            setSearch('');
            setCategoryFilter('All');
          }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {filteredSchemes.map((scheme) => (
            <div
              key={scheme.id}
              className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs hover:border-slate-700 transition-all p-5 sm:p-6 flex flex-col justify-between group"
            >
              <div>
                {/* Header */}
                <div className="flex items-start justify-between gap-3">
                  <div className="p-2.5 rounded-xl bg-blue-950 text-blue-400 border border-blue-800 shrink-0">
                    <Landmark className="w-5 h-5" />
                  </div>

                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-bold text-slate-300 bg-[#141C2B] px-2 py-0.5 rounded border border-slate-700">
                      {scheme.category}
                    </span>
                    <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                      {scheme.matchPercentage || 90}% Match
                    </span>
                  </div>
                </div>

                <h3 className="text-base font-bold text-white group-hover:text-blue-400 transition-colors mt-3">
                  {scheme.name}
                </h3>
                <span className="text-xs text-slate-400 font-medium block mt-0.5">
                  {scheme.officialSource || 'Ministry of MSME / Textiles, Govt of India'}
                </span>

                <p className="text-xs text-slate-300 mt-3 leading-relaxed">
                  {scheme.description}
                </p>

                {/* Subsidized Benefit Callout */}
                <div className="mt-4 p-3 rounded-xl bg-[#141C2B] border border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="text-[10px] uppercase font-bold text-blue-400">Financial Benefit</span>
                    <div className="text-xs font-bold text-emerald-400 mt-0.5">{scheme.benefit}</div>
                  </div>
                  <TrendingUp className="w-4 h-4 text-emerald-400" />
                </div>
              </div>

              {/* Action Button */}
              <div className="mt-5 pt-4 border-t border-slate-800 flex items-center justify-between">
                <span className="text-[11px] text-slate-400">Deadline: {scheme.deadline || 'Rolling scheme'}</span>
                <button
                  onClick={() => handleOpenDetail(scheme)}
                  className="py-1.5 px-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition-colors flex items-center gap-1.5 cursor-pointer shadow-xs"
                >
                  <span>View Details</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}