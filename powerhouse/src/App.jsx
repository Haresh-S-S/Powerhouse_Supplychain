import React, { useState } from 'react';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import Dashboard from './pages/Dashboard';
import BusinessProfile from './pages/BusinessProfile';
import BusinessAnalysisPage from './pages/BusinessAnalysisPage';
import ApprovalsLicences from './pages/ApprovalsLicences';
import ComplianceTasksPage from './pages/ComplianceTasksPage';
import DocumentsPage from './pages/DocumentsPage';
import ApplicationsPage from './pages/ApplicationsPage';
import GovernmentSchemesPage from './pages/GovernmentSchemesPage';
import AlertsPage from './pages/AlertsPage';
import ReportsPage from './pages/ReportsPage';
import SettingsPage from './pages/SettingsPage';
import AIComplianceAdvisorPage from './pages/AIComplianceAdvisorPage';
import {
  X,
  CheckCircle2,
  AlertTriangle,
  FileCheck,
  BrainCircuit,
  Loader2
} from 'lucide-react';
import Button from './components/ui/Button';
import { BusinessAnalysisProvider, useBusinessAnalysis } from './context/BusinessAnalysisContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import BusinessOnboarding from './pages/onboarding/BusinessOnboarding';
import LoginPage from './pages/auth/LoginPage';
import SignUpPage from './pages/auth/SignUpPage';
import WhyRequirementModal from './components/modals/WhyRequirementModal';
import ComplianceHealthModal from './components/modals/ComplianceHealthModal';
import WhyPriorityModal from './components/modals/WhyPriorityModal';
import ActionProposalModal from './components/modals/ActionProposalModal';
import CategoryComparisonModal from './components/modals/CategoryComparisonModal';
import AuditTrailModal from './components/modals/AuditTrailModal';
import UploadDocumentModal from './components/modals/UploadDocumentModal';
import DocumentDetailModal from './components/modals/DocumentDetailModal';
import GreenOperationsPage from './pages/GreenOperationsPage';
import SupplyChainPage from './pages/SupplyChainPage';
import WorkforcePage from './pages/WorkforcePage';
import WhyOpportunityModal from './components/modals/WhyOpportunityModal';
import GreenScoreExplainModal from './components/modals/GreenScoreExplainModal';
import WhySupplyRiskModal from './components/modals/WhySupplyRiskModal';
import WhySkillGapModal from './components/modals/WhySkillGapModal';

function MainAppContent() {
  const { logout, activeBusiness } = useAuth();
  const [activeNav, setActiveNav] = useState('overview');
  const [mobileOpen, setMobileOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    try {
      return localStorage.getItem('powerhouse_sidebar_collapsed') === 'true';
    } catch {
      return false;
    }
  });
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [modalState, setModalState] = useState({ isOpen: false, title: '', type: '', data: null });
  const [toastMessage, setToastMessage] = useState(null);

  const handleToggleSidebar = () => {
    setSidebarCollapsed((prev) => {
      const next = !prev;
      try {
        localStorage.setItem('powerhouse_sidebar_collapsed', String(next));
      } catch {
        // ignore localStorage errors
      }
      return next;
    });
  };

  const { isAnalyzing, currentStepIndex, analysisSteps, resetOnboarding, analysisResult, businessTemplateBundle } = useBusinessAnalysis();
  const activeBusinessName = analysisResult?.businessSummary?.businessName || 'your business';

  // Form states for modals
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskPriority, setNewTaskPriority] = useState('High');
  const [newTaskApproval, setNewTaskApproval] = useState('');

  const [newAppDept, setNewAppDept] = useState('');
  const [newAppTitle, setNewAppTitle] = useState('');

  // These dropdown option lists - and the "effective" selected value
  // that falls back to the first option - must always reflect the
  // active business's own data, never a leftover factory default.
  const approvalNameOptions = (businessTemplateBundle?.approvalsList || []).map((a) => a.name);
  const effectiveTaskApproval = approvalNameOptions.includes(newTaskApproval)
    ? newTaskApproval
    : (approvalNameOptions[0] || '');
  const departmentOptions = [...new Set((businessTemplateBundle?.applicationsList || []).map((a) => a.department))];
  const effectiveAppDept = departmentOptions.includes(newAppDept)
    ? newAppDept
    : (departmentOptions[0] || '');


  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 3500);
  };

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setIsRefreshing(false);
      showToast('All statutory compliance & application data refreshed successfully.');
    }, 800);
  };

  const handleContactSupport = () => {
    setModalState({
      isOpen: true,
      title: 'Powerhouse Dedicated Support',
      type: 'support',
      data: { message: 'Our compliance advisors are available 24/7 for filing assistance.' }
    });
  };

  const handleOpenNotification = (notif) => {
    setModalState({
      isOpen: true,
      title: notif.title || 'Notification Details',
      type: 'notification',
      data: notif
    });
  };

  const handleOpenProfile = (section) => {
    if (section === 'business') {
      setActiveNav('business-profile');
      showToast('Switched to Business Profile');
      return;
    }
    if (section === 'security') {
      setActiveNav('settings');
      showToast('Navigated to Compliance Settings');
      return;
    }
    setModalState({
      isOpen: true,
      title: 'Sign Out Confirmation',
      type: 'logout',
      data: { section }
    });
  };

  return (
    <div className="h-screen h-[100dvh] w-screen overflow-hidden flex bg-[#0B0F17] font-sans antialiased text-slate-100 selection:bg-blue-600 selection:text-white">
      {/* Toast Notification Container */}
      {toastMessage && (
        <div className="fixed bottom-5 right-5 z-50 bg-[#111827] text-white text-xs font-semibold px-4 py-3 rounded-xl shadow-2xl border border-[#1E293B] flex items-center gap-3 animate-in fade-in slide-in-from-bottom-3 duration-200">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>{toastMessage}</span>
          <button
            onClick={() => setToastMessage(null)}
            className="text-slate-400 hover:text-white ml-2 p-0.5 cursor-pointer"
            aria-label="Dismiss toast"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Realistic Multi-Step Analysis Loading Modal */}
      {isAnalyzing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-[#111827] rounded-3xl max-w-md w-full p-6 shadow-2xl border border-[#1E293B] space-y-5 animate-in zoom-in-95 duration-200">
            <div className="text-center space-y-1.5">
              <div className="w-12 h-12 rounded-2xl bg-blue-900/30 text-blue-400 border border-blue-800/50 flex items-center justify-center mx-auto shadow-xs">
                <BrainCircuit className="w-6 h-6 animate-pulse" />
              </div>
              <h3 className="font-bold text-slate-100 text-base">
                Executing Business Analysis Engine
              </h3>
              <p className="text-xs text-slate-400">
                Evaluating deterministic compliance rules for {activeBusinessName}...
              </p>
            </div>

            <div className="space-y-2.5 bg-[#141C2B] p-4 rounded-2xl border border-[#1E293B] text-xs font-medium">
              {analysisSteps.map((step, idx) => {
                const isPast = idx < currentStepIndex;
                const isCurrent = idx === currentStepIndex;

                return (
                  <div
                    key={idx}
                    className={`flex items-center gap-2.5 transition-all duration-150 ${
                      isPast
                        ? 'text-emerald-400 font-semibold'
                        : isCurrent
                        ? 'text-blue-400 font-bold'
                        : 'text-slate-500 opacity-60'
                    }`}
                  >
                    {isPast ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    ) : isCurrent ? (
                      <Loader2 className="w-4 h-4 text-blue-400 animate-spin shrink-0" />
                    ) : (
                      <span className="w-4 h-4 rounded-full border border-slate-700 flex items-center justify-center text-[9px] shrink-0 text-slate-500">
                        {idx + 1}
                      </span>
                    )}
                    <span className="truncate">{step}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Main Sidebar (pinned height, never scrolls with page) */}
      <Sidebar
        activeNav={activeNav}
        setActiveNav={(nav) => {
          setActiveNav(nav);
        }}
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
        onContactSupport={handleContactSupport}
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={handleToggleSidebar}
      />

      {/* Main Content Column: Top header pinned, main viewport independently scrolls */}
      <div className="flex-1 h-full min-w-0 flex flex-col overflow-hidden">
        {/* Sticky Top Header */}
        <Header
          onRefresh={handleRefresh}
          isRefreshing={isRefreshing}
          onOpenMobileMenu={() => setMobileOpen(true)}
          onOpenProfile={handleOpenProfile}
          onOpenNotification={handleOpenNotification}
          onContactSupport={handleContactSupport}
          isSidebarCollapsed={sidebarCollapsed}
          onToggleSidebar={handleToggleSidebar}
        />

        {/* Page Content Viewport - Only this scrolls */}
        <main className="flex-1 min-h-0 overflow-y-auto w-full px-2.5 sm:px-3.5 py-2.5 scrollbar-thin">
          <div className="max-w-[1680px] mx-auto w-full space-y-2.5">
            {(activeNav === 'dashboard' || activeNav === 'overview') && (
              <Dashboard
                modalState={modalState}
                setModalState={setModalState}
                onNavigate={(route) => setActiveNav(route)}
              />
            )}

          {activeNav === 'ai' && (
            <AIComplianceAdvisorPage
              onNavigate={(route) => setActiveNav(route)}
              showToast={showToast}
              setModalState={setModalState}
            />
          )}

          {activeNav === 'business-profile' && (
            <BusinessProfile
              showToast={showToast}
              setModalState={setModalState}
              onNavigate={(route) => setActiveNav(route)}
            />
          )}

          {activeNav === 'business-analysis' && (
            <BusinessAnalysisPage
              onNavigate={(route) => setActiveNav(route)}
              showToast={showToast}
              setModalState={setModalState}
            />
          )}

          {activeNav === 'approvals' && (
            <ApprovalsLicences
              onNavigateToRoadmap={() => setActiveNav('overview')}
              setModalState={setModalState}
              showToast={showToast}
            />
          )}

          {activeNav === 'compliance-tasks' && (
            <ComplianceTasksPage
              showToast={showToast}
              setModalState={setModalState}
            />
          )}

          {activeNav === 'documents' && (
            <DocumentsPage
              showToast={showToast}
              setModalState={setModalState}
            />
          )}

          {activeNav === 'applications' && (
            <ApplicationsPage
              showToast={showToast}
              setModalState={setModalState}
            />
          )}

          {activeNav === 'government-schemes' && (
            <GovernmentSchemesPage
              showToast={showToast}
              setModalState={setModalState}
            />
          )}

          {activeNav === 'alerts' && (
            <AlertsPage
              onNavigate={(route) => setActiveNav(route)}
              showToast={showToast}
              setModalState={setModalState}
            />
          )}

          {activeNav === 'reports' && (
            <ReportsPage
              showToast={showToast}
              setModalState={setModalState}
            />
          )}

          {activeNav === 'settings' && (
            <SettingsPage
              onNavigateToProfile={() => setActiveNav('business-profile')}
              showToast={showToast}
              setModalState={setModalState}
            />
          )}

          {activeNav === 'green-flow' && (
            <GreenOperationsPage
              showToast={showToast}
              onNavigate={setActiveNav}
              setModalState={setModalState}
            />
          )}

          {activeNav === 'supply-chain' && (
            <SupplyChainPage
              showToast={showToast}
              onNavigate={setActiveNav}
              setModalState={setModalState}
            />
          )}

          {activeNav === 'workforce' && (
            <WorkforcePage
              showToast={showToast}
              onNavigate={setActiveNav}
              setModalState={setModalState}
            />
          )}
          </div>
        </main>
      </div>

      {/* Explainable Compliance Intelligence Modals */}
      {modalState.isOpen && modalState.type === 'why-requirement' && (
        <WhyRequirementModal
          isOpen={true}
          onClose={() => setModalState({ isOpen: false, title: '', type: '', data: null })}
          approval={modalState.data?.approval || modalState.data}
          businessProfile={modalState.data?.businessProfile || analysisResult?.businessSummary}
        />
      )}

      {modalState.isOpen && modalState.type === 'compliance-health' && (
        <ComplianceHealthModal
          isOpen={true}
          onClose={() => setModalState({ isOpen: false, title: '', type: '', data: null })}
          breakdownData={modalState.data}
          totalScore={modalState.data?.score || 92}
        />
      )}

      {modalState.isOpen && modalState.type === 'why-priority' && (
        <WhyPriorityModal
          isOpen={true}
          onClose={() => setModalState({ isOpen: false, title: '', type: '', data: null })}
          priorityItem={modalState.data}
        />
      )}

      {modalState.isOpen && modalState.type === 'action-proposal' && (
        <ActionProposalModal
          isOpen={true}
          onClose={() => setModalState({ isOpen: false, title: '', type: '', data: null })}
          proposal={modalState.data?.proposal || modalState.data}
          onActionApproved={(res) => {
            showToast('Human-in-the-loop action executed and committed to Audit Trail.');
            if (modalState.data?.onApproved) modalState.data.onApproved(res);
          }}
          onActionRejected={() => {
            showToast('Action rejected by user and recorded.');
          }}
        />
      )}

      {modalState.isOpen && modalState.type === 'category-comparison' && (
        <CategoryComparisonModal
          isOpen={true}
          onClose={() => setModalState({ isOpen: false, title: '', type: '', data: null })}
          initialCategoryA={modalState.data?.catA || 'factory'}
          initialCategoryB={modalState.data?.catB || 'restaurant'}
          city={analysisResult?.businessSummary?.city || 'Tiruppur'}
          state={analysisResult?.businessSummary?.state || 'Tamil Nadu'}
        />
      )}

      {modalState.isOpen && modalState.type === 'audit-trail' && (
        <AuditTrailModal
          isOpen={true}
          onClose={() => setModalState({ isOpen: false, title: '', type: '', data: null })}
          userName="Mohith K"
        />
      )}

      {/* Upload Business Document Modal */}
      {modalState.isOpen && modalState.type === 'upload-document' && (
        <UploadDocumentModal
          isOpen={true}
          onClose={() => setModalState({ isOpen: false, title: '', type: '', data: null })}
          businessProfileId={modalState.data?.businessProfileId || activeBusiness?.id}
          approvalsList={modalState.data?.approvalsList || businessTemplateBundle?.approvalsList || []}
          onUploadSuccess={(newDoc) => {
            if (modalState.data?.onUpload) {
              modalState.data.onUpload(newDoc);
            }
          }}
          showToast={showToast}
        />
      )}

      {/* Document Detail & Intelligence Modal */}
      {modalState.isOpen && modalState.type === 'document-detail' && (
        <DocumentDetailModal
          isOpen={true}
          onClose={() => setModalState({ isOpen: false, title: '', type: '', data: null })}
          document={modalState.data}
          showToast={showToast}
          onDeleteSuccess={(deletedId) => {
            if (modalState.data?.onDelete) {
              modalState.data.onDelete(deletedId);
            }
          }}
        />
      )}

      {/* Why Green Opportunity Modal (Explainability Trace) */}
      {modalState.isOpen && modalState.type === 'why-green-opportunity' && (
        <WhyOpportunityModal
          isOpen={true}
          onClose={() => setModalState({ isOpen: false, title: '', type: '', data: null })}
          opportunity={modalState.data}
        />
      )}

      {/* Why Green Score Modal (5-Pillar Breakdown) */}
      {modalState.isOpen && modalState.type === 'why-green-score' && (
        <GreenScoreExplainModal
          isOpen={true}
          onClose={() => setModalState({ isOpen: false, title: '', type: '', data: null })}
          scoreDetail={modalState.data?.scoreDetail}
        />
      )}

      {/* Why Supply Risk Modal (7-Stage Explainability) */}
      {modalState.isOpen && modalState.type === 'why-supply-risk' && (
        <WhySupplyRiskModal
          isOpen={true}
          onClose={() => setModalState({ isOpen: false, title: '', type: '', data: null })}
          risk={modalState.data?.risk || modalState.data}
          onActionProposal={modalState.data?.onActionProposal}
        />
      )}

      {/* Why Skill Gap Modal (Competency & Inclusion Explainability) */}
      {modalState.isOpen && modalState.type === 'why-skill-gap' && (
        <WhySkillGapModal
          isOpen={true}
          onClose={() => setModalState({ isOpen: false, title: '', type: '', data: null })}
          skillGap={modalState.data?.skillGap || modalState.data}
          onActionProposal={modalState.data?.onActionProposal}
        />
      )}

      {/* Global Interactive Modals for Standard Application Views */}
      {modalState.isOpen && !['why-requirement', 'compliance-health', 'why-priority', 'action-proposal', 'category-comparison', 'audit-trail', 'upload-document', 'document-detail', 'why-green-opportunity', 'why-green-score', 'why-supply-risk', 'why-skill-gap'].includes(modalState.type) && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-xs animate-in fade-in duration-150"
          onClick={() => setModalState({ isOpen: false, title: '', type: '', data: null })}
          role="dialog"
          aria-modal="true"
        >
          <div
            className="bg-[#111827] rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-[#1E293B] text-slate-100 relative animate-in zoom-in-95 duration-150 max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-blue-900/30 text-blue-400 flex items-center justify-center border border-blue-800/50">
                  <FileCheck className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-100 text-base">{modalState.title}</h3>
                  <span className="text-[11px] text-slate-400">POWER HOUSE Intelligence View</span>
                </div>
              </div>
              <button
                onClick={() => setModalState({ isOpen: false, title: '', type: '', data: null })}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
                aria-label="Close dialog"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Content Router by type */}
            <div className="py-5 text-sm text-slate-300 space-y-4">
              {modalState.type === 'stat' && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3.5 rounded-xl bg-[#141C2B] border border-[#1E293B]">
                    <span className="text-xs font-semibold text-slate-400 uppercase">Current Metric</span>
                    <span className="text-2xl font-bold text-slate-100">{modalState.data?.value}</span>
                  </div>
                  <p className="text-xs leading-relaxed text-slate-400">
                    This metric is continuously calculated based on active statutory mandates, factory inspections, and recurring compliance calendars.
                  </p>
                </div>
              )}

              {modalState.type === 'approval-detail' && (
                <div className="space-y-3">
                  <div className="p-3.5 bg-[#141C2B] border border-[#1E293B] rounded-xl space-y-1.5">
                    <div className="text-xs text-slate-400 font-medium">Authority & Category</div>
                    <div className="font-bold text-slate-100">{modalState.data?.authority} • {modalState.data?.category}</div>
                    <p className="text-xs text-slate-300 mt-2">{modalState.data?.description}</p>
                  </div>
                  <div className="space-y-2">
                    <div className="text-xs font-bold text-slate-100">Application Milestones</div>
                    <div className="space-y-1.5">
                      {modalState.data?.steps?.map((st, i) => (
                        <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-[#0B0F17] border border-[#1E293B] text-xs">
                          <span className="text-slate-300">{st.name}</span>
                          <span className="font-bold text-blue-400">{st.status}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {modalState.type === 'add-task' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-300 mb-1">Task Title</label>
                    <input
                      type="text"
                      placeholder="e.g. Renew business registration certificate"
                      value={newTaskTitle}
                      onChange={(e) => setNewTaskTitle(e.target.value)}
                      className="w-full px-3 py-2 text-xs rounded-xl bg-[#141C2B] border border-[#1E293B] text-slate-100 placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-300 mb-1">Related License</label>
                    <select
                      value={effectiveTaskApproval}
                      onChange={(e) => setNewTaskApproval(e.target.value)}
                      className="w-full px-3 py-2 text-xs rounded-xl bg-[#141C2B] border border-[#1E293B] text-slate-100 focus:border-blue-500 focus:outline-none"
                    >
                      {approvalNameOptions.map((name) => (
                        <option key={name} value={name} className="bg-[#111827] text-slate-100">{name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-300 mb-1">Priority</label>
                    <div className="flex gap-2">
                      {['High', 'Medium', 'Low'].map((p) => (
                        <button
                          key={p}
                          type="button"
                          onClick={() => setNewTaskPriority(p)}
                          className={`px-3 py-1.5 rounded-lg text-xs font-bold cursor-pointer transition-colors ${
                            newTaskPriority === p
                              ? 'bg-blue-600 text-white'
                              : 'bg-[#141C2B] text-slate-400 border border-[#1E293B] hover:text-slate-200'
                          }`}
                        >
                          {p}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {modalState.type === 'task-detail' && (
                <div className="space-y-3">
                  <div className="p-3.5 bg-[#141C2B] rounded-xl border border-[#1E293B] space-y-1">
                    <div className="text-xs font-bold text-slate-100">{modalState.data?.title}</div>
                    <div className="text-xs text-slate-400">{modalState.data?.description}</div>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="p-2.5 bg-[#0B0F17] border border-[#1E293B] rounded-lg">
                      <span className="text-slate-500 block text-[10px]">Assignee</span>
                      <span className="font-bold text-slate-200">{modalState.data?.assignee}</span>
                    </div>
                    <div className="p-2.5 bg-[#0B0F17] border border-[#1E293B] rounded-lg">
                      <span className="text-slate-500 block text-[10px]">Due Date</span>
                      <span className="font-bold text-slate-200">{modalState.data?.dueDate}</span>
                    </div>
                  </div>
                </div>
              )}

              {modalState.type === 'new-application' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-300 mb-1">Target Department</label>
                    <select
                      value={effectiveAppDept}
                      onChange={(e) => setNewAppDept(e.target.value)}
                      className="w-full px-3 py-2 text-xs rounded-xl bg-[#141C2B] border border-[#1E293B] text-slate-100 focus:border-blue-500 focus:outline-none"
                    >
                      {departmentOptions.map((dept) => (
                        <option key={dept} value={dept} className="bg-[#111827]">{dept}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-300 mb-1">Application Title</label>
                    <input
                      type="text"
                      placeholder="e.g. Additional registration consent"
                      value={newAppTitle}
                      onChange={(e) => setNewAppTitle(e.target.value)}
                      className="w-full px-3 py-2 text-xs rounded-xl bg-[#141C2B] border border-[#1E293B] text-slate-100 placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                    />
                  </div>
                </div>
              )}

              {modalState.type === 'application-timeline' && (
                <div className="space-y-4">
                  <div className="p-3 bg-[#141C2B] rounded-xl border border-[#1E293B]">
                    <div className="font-bold text-slate-100">{modalState.data?.application}</div>
                    <div className="text-xs text-slate-400">{modalState.data?.department} • Ref: {modalState.data?.referenceNo}</div>
                  </div>

                  <div>
                    <div className="font-bold text-xs text-slate-200 mb-2">Stage Progression</div>
                    <div className="space-y-2">
                      {modalState.data?.stages?.map((stage, idx) => {
                        const isCurrent = stage === modalState.data?.currentStage;

                        return (
                          <div
                            key={stage}
                            className={`flex items-center gap-3 p-2.5 rounded-xl text-xs ${
                              isCurrent
                                ? 'bg-blue-950/50 text-blue-300 font-bold border border-blue-800/60'
                                : 'text-slate-400 bg-[#0B0F17] border border-[#1E293B]'
                            }`}
                          >
                            <span className="w-5 h-5 rounded-full bg-[#141C2B] flex items-center justify-center text-[10px] font-bold border border-slate-700 text-slate-300">
                              {idx + 1}
                            </span>
                            <span>{stage}</span>
                            {isCurrent && <span className="ml-auto text-[10px] text-blue-400 uppercase font-bold">Active Stage</span>}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}

              {modalState.type === 'scheme-detail' && (
                <div className="space-y-3">
                  <div className="p-3.5 bg-blue-950/40 border border-blue-800/60 rounded-xl">
                    <div className="text-xs font-bold text-blue-300">Direct Subsidy Benefit</div>
                    <div className="text-lg font-black text-blue-100 mt-0.5">{modalState.data?.benefit}</div>
                  </div>
                  <div>
                    <div className="font-bold text-slate-200 text-xs mb-1">Key Eligibility Criteria</div>
                    <ul className="list-disc list-inside text-slate-400 text-xs space-y-1">
                      {modalState.data?.eligibility?.map((e, i) => (
                        <li key={i}>{e}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {modalState.type === 'report-generate' && (
                <div className="space-y-3">
                  <div className="p-4 bg-emerald-950/40 rounded-xl border border-emerald-800/60 text-center space-y-1">
                    <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
                    <div className="font-bold text-emerald-100 text-base">Executive Dossier Generated</div>
                    <div className="text-xs text-emerald-400">Verified for compliance audit requirements</div>
                  </div>
                  <div className="p-3 bg-[#141C2B] rounded-xl border border-[#1E293B] text-xs space-y-1 text-slate-300">
                    <div>Organization: <strong className="text-slate-100">{modalState.data?.company}</strong></div>
                    <div>Statutory Score: <strong className="text-slate-100">{modalState.data?.score}</strong></div>
                    <div>Date of Compilation: <strong className="text-slate-100">{modalState.data?.generatedOn}</strong></div>
                  </div>
                </div>
              )}

              {modalState.type === 'delete-confirm' && (
                <div className="p-4 bg-rose-950/40 border border-rose-800/60 rounded-xl text-rose-300 text-xs flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                  <span>{modalState.data?.message}</span>
                </div>
              )}

              {modalState.type === 'support' && (
                <div className="space-y-3 text-xs leading-relaxed">
                  <p className="text-slate-300">{modalState.data?.message}</p>
                  <div className="p-3 bg-[#141C2B] rounded-xl border border-[#1E293B] space-y-1 text-slate-300">
                    <div>Toll-free Hotline: <strong className="text-slate-100">1800-419-7000</strong></div>
                    <div>Support Desk: <strong className="text-slate-100">compliance@powerhouse.in</strong></div>
                    <div>Working Hours: <strong className="text-slate-100">Mon - Sat (9:00 AM - 7:00 PM IST)</strong></div>
                  </div>
                </div>
              )}

              {modalState.type === 'logout' && (
                <p className="text-xs leading-relaxed text-slate-300">
                  You&apos;ll be signed out and returned to the business classification screen.
                  Your current business type is remembered, so you can pick up right where you
                  left off, or describe a different business next time.
                </p>
              )}

              {modalState.type === 'switch-business' && (
                <p className="text-xs leading-relaxed text-slate-300">{modalState.data?.message}</p>
              )}
            </div>

            {/* Modal Footer Actions */}
            <div className="pt-4 border-t border-slate-800 flex justify-end gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setModalState({ isOpen: false, title: '', type: '', data: null })}
                className="text-xs font-semibold"
              >
                Close
              </Button>

              {modalState.type === 'add-task' && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => {
                    if (!newTaskTitle) return;
                    modalState.data?.onAdd({
                      id: `task-${Date.now()}`,
                      title: newTaskTitle,
                      relatedApproval: effectiveTaskApproval,
                      priority: newTaskPriority,
                      dueDate: 'Due in 14 days',
                      status: 'Upcoming',
                      assignee: 'Business Owner',
                      completed: false,
                    });
                    setNewTaskTitle('');
                    setModalState({ isOpen: false, title: '', type: '', data: null });
                  }}
                  className="text-xs font-semibold"
                >
                  Create Task
                </Button>
              )}

              {modalState.type === 'logout' && (
                <Button
                  variant="danger"
                  size="sm"
                  onClick={async () => {
                    setModalState({ isOpen: false, title: '', type: '', data: null });
                    await logout();
                  }}
                  className="text-xs font-semibold"
                >
                  Sign Out
                </Button>
              )}

              {modalState.type === 'switch-business' && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => {
                    setModalState({ isOpen: false, title: '', type: '', data: null });
                    resetOnboarding();
                  }}
                  className="text-xs font-semibold"
                >
                  Continue
                </Button>
              )}

              {modalState.type === 'new-application' && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => {
                    if (!newAppTitle) return;
                    modalState.data?.onSubmit({
                      id: `APP-2024-00${Math.floor(Math.random() * 90 + 10)}`,
                      department: effectiveAppDept,
                      application: newAppTitle,
                      status: 'Submitted',
                      submissionDate: 'Just now',
                      updatedOn: 'Just now',
                      referenceNo: `REG/${Date.now().toString().slice(-4)}`,
                      currentStage: 'Submitted',
                      stages: ['Draft', 'Submitted', 'Under Review', 'Additional Documents', 'Approved'],
                    });
                    setNewAppTitle('');
                    setModalState({ isOpen: false, title: '', type: '', data: null });
                  }}
                  className="text-xs font-semibold"
                >
                  Submit Application
                </Button>
              )}

              {modalState.type === 'delete-confirm' && (
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => {
                    showToast('Local prototype data purged.');
                    setModalState({ isOpen: false, title: '', type: '', data: null });
                  }}
                  className="text-xs font-semibold"
                >
                  Confirm Reset
                </Button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function AppGate() {
  const { isAuthenticated, isLoading, onboardingCompleted } = useAuth();
  const { onboardingComplete } = useBusinessAnalysis();
  const [authView, setAuthView] = useState('login'); // 'login' | 'signup'

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0B0F17] flex flex-col items-center justify-center font-sans antialiased text-slate-100 p-4 selection:bg-blue-600 selection:text-white">
        <div className="flex flex-col items-center space-y-4 animate-in fade-in duration-300">
          <div className="w-14 h-14 rounded-2xl overflow-hidden bg-black border border-amber-500/30 flex items-center justify-center shadow-xl shadow-amber-500/10 p-1.5">
            <img src="/logo.png" alt="POWER HOUSE" className="w-full h-full object-contain" />
          </div>
          <div className="text-center space-y-1">
            <span className="text-sm font-bold text-white tracking-widest uppercase block leading-none">
              POWER HOUSE
            </span>
            <span className="text-[11px] text-slate-400 font-medium tracking-normal mt-1 block">
              Compliance. Simplified.
            </span>
          </div>
          <div className="flex items-center gap-2.5 text-xs text-blue-400 pt-3">
            <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
            <span className="font-medium text-slate-300">Loading your workspace…</span>
          </div>
        </div>
      </div>
    );
  }

  // 1. Unauthenticated -> Login / Sign Up
  if (!isAuthenticated) {
    if (authView === 'signup') {
      return <SignUpPage onNavigateToLogin={() => setAuthView('login')} />;
    }
    return <LoginPage onNavigateToSignup={() => setAuthView('signup')} />;
  }

  // 2. Incomplete onboarding -> BusinessOnboarding
  if (!onboardingCompleted && !onboardingComplete) {
    return <BusinessOnboarding />;
  }

  // 3. Completed onboarding -> MainAppContent (Tailored Dashboard & Workspace)
  return <MainAppContent />;
}

export default function App() {
  return (
    <AuthProvider>
      <BusinessAnalysisProvider>
        <AppGate />
      </BusinessAnalysisProvider>
    </AuthProvider>
  );
}