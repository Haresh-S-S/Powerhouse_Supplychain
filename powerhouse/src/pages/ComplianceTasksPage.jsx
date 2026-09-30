import React, { useState } from 'react';
import {
  CheckSquare,
  CheckCircle2,
  Clock,
  Calendar,
  Plus,
  User,
  ChevronRight,
  Check
} from 'lucide-react';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import SearchInput from '../components/ui/SearchInput';
import EmptyState from '../components/ui/EmptyState';
import { useBusinessAnalysis } from '../context/BusinessAnalysisContext';

export default function ComplianceTasksPage({ showToast, setModalState }) {
  const { businessTemplateBundle } = useBusinessAnalysis();
  const [tasks, setTasks] = useState(businessTemplateBundle.tasksList);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [priorityFilter, setPriorityFilter] = useState('All');

  const totalCount = tasks.length;
  const completedCount = tasks.filter((t) => t.completed || t.status === 'Completed').length;
  const inProgressCount = tasks.filter((t) => (t.status === 'In Progress' || t.status === 'Upcoming') && !t.completed).length;
  const upcomingCount = tasks.filter((t) => t.status === 'Overdue' || !t.completed).length;

  const handleToggleTask = (id) => {
    setTasks((prev) =>
      prev.map((t) => {
        if (t.id === id) {
          const nextState = !t.completed;
          showToast(nextState ? 'Task marked as completed.' : 'Task moved to pending.');
          return {
            ...t,
            completed: nextState,
            status: nextState ? 'Completed' : 'Upcoming',
          };
        }
        return t;
      })
    );
  };

  const handleOpenTaskDetail = (task) => {
    setModalState({
      isOpen: true,
      title: task.title,
      type: 'task-detail',
      data: task,
    });
  };

  const handleOpenAddTask = () => {
    setModalState({
      isOpen: true,
      title: 'Create Compliance Task',
      type: 'add-task',
      data: {
        onAdd: (newTask) => {
          setTasks((prev) => [newTask, ...prev]);
          showToast('New compliance task created successfully.');
        },
      },
    });
  };

  const filteredTasks = tasks.filter((t) => {
    const matchSearch = t.title.toLowerCase().includes(search.toLowerCase()) ||
      (t.relatedApproval && t.relatedApproval.toLowerCase().includes(search.toLowerCase())) ||
      (t.subtext && t.subtext.toLowerCase().includes(search.toLowerCase())) ||
      (t.assignee && t.assignee.toLowerCase().includes(search.toLowerCase()));
    const matchStatus = statusFilter === 'All' ||
      (statusFilter === 'Completed' && (t.completed || t.status === 'Completed')) ||
      (statusFilter === 'In Progress' && t.status === 'In Progress' && !t.completed) ||
      (statusFilter === 'Upcoming' && (t.status === 'Upcoming' || t.status === 'Overdue') && !t.completed);
    const matchPriority = priorityFilter === 'All' || t.priority === priorityFilter;
    return matchSearch && matchStatus && matchPriority;
  });

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-1">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Compliance Tasks
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
            Track and execute your business compliance calendars and statutory filings.
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          onClick={handleOpenAddTask}
          className="self-start sm:self-auto text-xs font-semibold"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Add Task</span>
        </Button>
      </div>

      {/* Top Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5 sm:gap-5">
        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-400">Total Tasks</div>
            <div className="text-xl sm:text-2xl font-black text-white mt-1">{totalCount}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Active schedule</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-950/80 text-blue-400 flex items-center justify-center border border-blue-800/80 shrink-0">
            <CheckSquare className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-400">Completed</div>
            <div className="text-xl sm:text-2xl font-black text-emerald-400 mt-1">{completedCount}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Filed on schedule</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-950/80 text-emerald-400 flex items-center justify-center border border-emerald-800/80 shrink-0">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-400">In Progress / Due Soon</div>
            <div className="text-xl sm:text-2xl font-black text-blue-400 mt-1">{inProgressCount}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Under filing window</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-950/80 text-blue-400 flex items-center justify-center border border-blue-800/80 shrink-0">
            <Clock className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-400">Overdue / Critical</div>
            <div className="text-xl sm:text-2xl font-black text-rose-400 mt-1">{tasks.filter((t) => t.status === 'Overdue').length || 2}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Action required</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-rose-950/80 text-rose-400 flex items-center justify-center border border-rose-800/80 shrink-0">
            <Calendar className="w-5 h-5" />
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
            placeholder="Search tasks, departments, assignees..."
          />
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 text-xs font-medium rounded-xl border border-[#1E293B] bg-[#141C2B] hover:border-slate-700 focus:border-blue-500 focus:outline-none transition-all text-slate-200"
          >
            <option value="All">All Statuses</option>
            <option value="Upcoming">Upcoming / Overdue</option>
            <option value="In Progress">In Progress</option>
            <option value="Completed">Completed</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-3 py-2 text-xs font-medium rounded-xl border border-[#1E293B] bg-[#141C2B] hover:border-slate-700 focus:border-blue-500 focus:outline-none transition-all text-slate-200"
          >
            <option value="All">All Priorities</option>
            <option value="High">High Priority</option>
            <option value="Medium">Medium Priority</option>
            <option value="Low">Low Priority</option>
          </select>
        </div>
      </div>

      {/* Task List */}
      {filteredTasks.length === 0 ? (
        <EmptyState
          title="No compliance tasks match your filter"
          description="Try resetting your search query or selecting 'All' for status and priority filters."
          actionLabel="Clear Filters"
          onAction={() => {
            setSearch('');
            setStatusFilter('All');
            setPriorityFilter('All');
          }}
        />
      ) : (
        <div className="space-y-3">
          {filteredTasks.map((task) => (
            <div
              key={task.id}
              className={`p-4 rounded-2xl border transition-all duration-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
                task.completed
                  ? 'bg-[#141C2B]/40 border-slate-800 opacity-75'
                  : 'bg-[#111827] border-[#1E293B] hover:border-slate-700'
              }`}
            >
              <div className="flex items-start gap-3.5 flex-1 min-w-0">
                {/* Custom Checkbox */}
                <button
                  type="button"
                  onClick={() => handleToggleTask(task.id)}
                  className={`w-5 h-5 rounded-lg border flex items-center justify-center transition-all cursor-pointer shrink-0 mt-0.5 ${
                    task.completed
                      ? 'bg-emerald-600 border-emerald-600 text-white shadow-xs'
                      : 'border-slate-600 hover:border-blue-500 bg-[#141C2B]'
                  }`}
                  aria-label={task.completed ? 'Mark task pending' : 'Mark task completed'}
                >
                  {task.completed && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                </button>

                <div className="space-y-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span
                      className={`text-sm font-semibold truncate ${
                        task.completed ? 'line-through text-slate-500' : 'text-white'
                      }`}
                    >
                      {task.title}
                    </span>
                    <Badge variant={task.status} size="xs" withDot>
                      {task.statusText || task.status}
                    </Badge>
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                        task.priority === 'High'
                          ? 'bg-rose-950/80 text-rose-400 border border-rose-800/80'
                          : 'bg-[#141C2B] text-slate-300 border border-slate-700'
                      }`}
                    >
                      {task.priority} Priority
                    </span>
                  </div>

                  <p className="text-xs text-slate-400 leading-snug">
                    {task.subtext || task.description || task.relatedApproval}
                  </p>

                  <div className="flex items-center gap-4 text-[11px] text-slate-400 pt-1 flex-wrap">
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3 text-slate-400" />
                      <span className={task.status === 'Overdue' ? 'text-rose-400 font-semibold' : ''}>
                        {task.statusText || task.dueDate}
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      <User className="w-3 h-3 text-slate-400" />
                      <span>{task.assignee || 'Business Owner'}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 self-end sm:self-center">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleOpenTaskDetail(task)}
                  className="text-xs text-slate-300 hover:text-white"
                >
                  <span>Details</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}