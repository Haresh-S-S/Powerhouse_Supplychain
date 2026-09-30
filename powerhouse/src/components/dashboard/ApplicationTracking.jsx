import React, { useState } from 'react';
import {
  FileCheck2,
  MoreHorizontal,
  ChevronRight,
  Search,
  Clock
} from 'lucide-react';
import Badge from '../ui/Badge';
import Button from '../ui/Button';

export default function ApplicationTracking({
  applications,
  onViewAll,
  onActionClick,
}) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredApps = applications.filter(
    (app) =>
      app.application.toLowerCase().includes(searchTerm.toLowerCase()) ||
      app.department.toLowerCase().includes(searchTerm.toLowerCase()) ||
      app.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs p-5 sm:p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-slate-100">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-blue-50 text-blue-600 border border-blue-100">
            <FileCheck2 className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-base sm:text-lg font-bold text-slate-900 leading-none">
              Application Tracking
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Live status of state and central department approvals
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5 self-start sm:self-auto">
          {/* Quick Search */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search applications..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8 pr-3 py-1.5 text-xs rounded-lg border border-slate-200 bg-slate-50/50 hover:bg-white focus:bg-white focus:border-blue-500 focus:outline-none w-36 sm:w-48 transition-all"
            />
          </div>

          <Button
            variant="secondary"
            size="sm"
            onClick={onViewAll}
            className="text-xs font-semibold text-blue-600 hover:text-blue-700"
          >
            <span>View All</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>

      {/* Desktop & Tablet Table */}
      <div className="hidden md:block overflow-x-auto mt-4">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-200/80 text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
              <th className="py-3 px-3">Application ID</th>
              <th className="py-3 px-3">Department</th>
              <th className="py-3 px-3">Application</th>
              <th className="py-3 px-3">Status</th>
              <th className="py-3 px-3">Updated On</th>
              <th className="py-3 px-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
            {filteredApps.map((item) => (
              <tr
                key={item.id}
                className="hover:bg-slate-50/80 transition-colors group"
              >
                <td className="py-3.5 px-3">
                  <span className="font-mono text-slate-900 font-semibold text-[11px] bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                    {item.id}
                  </span>
                </td>
                <td className="py-3.5 px-3 text-slate-600">{item.department}</td>
                <td className="py-3.5 px-3 font-semibold text-slate-900 group-hover:text-blue-600 transition-colors">
                  {item.application}
                </td>
                <td className="py-3.5 px-3">
                  <Badge variant={item.status} withDot>
                    {item.status}
                  </Badge>
                </td>
                <td className="py-3.5 px-3 text-slate-500">{item.updatedOn}</td>
                <td className="py-3.5 px-3 text-right relative">
                  <button
                    onClick={() => onActionClick(item)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 border border-transparent hover:border-slate-200 transition-colors cursor-pointer"
                    aria-label={`Actions for ${item.application}`}
                  >
                    <MoreHorizontal className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile Card Transform View */}
      <div className="md:hidden mt-4 space-y-3">
        {filteredApps.map((item) => (
          <div
            key={item.id}
            className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-white transition-all space-y-3"
          >
            <div className="flex items-center justify-between">
              <span className="font-mono text-[11px] font-semibold text-slate-700 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                {item.id}
              </span>
              <Badge variant={item.status} withDot size="xs">
                {item.status}
              </Badge>
            </div>

            <div>
              <h3 className="font-semibold text-slate-900 text-sm">
                {item.application}
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">{item.department}</p>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-slate-200/60 text-xs text-slate-500">
              <div className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                <span>Updated: {item.updatedOn}</span>
              </div>
              <button
                onClick={() => onActionClick(item)}
                className="text-xs font-semibold text-blue-600 hover:text-blue-800"
              >
                View Details
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
