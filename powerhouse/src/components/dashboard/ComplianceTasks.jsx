import React from 'react';
import {
  ClipboardList,
  Clock,
  ChevronRight,
  CheckCircle2
} from 'lucide-react';
import Badge from '../ui/Badge';
import Button from '../ui/Button';

export default function ComplianceTasks({ tasks, onViewAll }) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs p-5 sm:p-6 flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-orange-50 text-orange-600 border border-orange-100">
              <ClipboardList className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base sm:text-lg font-bold text-slate-900 leading-none">
                Compliance Tasks
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Upcoming regulatory filings & statutory requirements
              </p>
            </div>
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

        {/* Task Rows */}
        <div className="mt-4 divide-y divide-slate-100">
          {tasks.map((task) => (
            <div
              key={task.id}
              className="py-3.5 first:pt-2 last:pb-1 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 group hover:bg-slate-50/70 rounded-xl px-2.5 transition-colors -mx-2.5 cursor-pointer"
            >
              <div className="flex items-start gap-3">
                <div className="mt-0.5">
                  {task.status === 'Completed' ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                  ) : (
                    <Clock className="w-4 h-4 text-slate-400 group-hover:text-blue-500 transition-colors shrink-0" />
                  )}
                </div>
                <div>
                  <h3 className="text-xs sm:text-sm font-semibold text-slate-800 group-hover:text-blue-600 transition-colors">
                    {task.title}
                  </h3>
                  <div className="flex items-center gap-2 mt-0.5 text-xs text-slate-500">
                    <span className="text-[11px] font-medium text-slate-500">
                      {task.due}
                    </span>
                    {task.priority && (
                      <span className="text-[10px] text-slate-400">
                        • Priority: {task.priority}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="self-start sm:self-center">
                <Badge variant={task.status} withDot>
                  {task.status}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 bg-slate-50/50 p-2.5 rounded-lg border border-slate-100">
        <span className="text-[11px] font-medium text-slate-600">
          Auto-reminders enabled for authorized signatory
        </span>
        <span className="font-semibold text-emerald-600 text-[11px]">
          All Active
        </span>
      </div>
    </div>
  );
}
