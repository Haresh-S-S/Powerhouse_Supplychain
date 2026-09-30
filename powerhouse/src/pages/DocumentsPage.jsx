import React, { useState, useEffect } from 'react';
import {
  FolderKanban,
  FileCheck,
  Clock,
  XCircle,
  UploadCloud,
  Eye,
  Download,
  ShieldCheck
} from 'lucide-react';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import SearchInput from '../components/ui/SearchInput';
import EmptyState from '../components/ui/EmptyState';
import { useBusinessAnalysis } from '../context/BusinessAnalysisContext';
import { useAuth } from '../context/AuthContext';
import apiClient from '../services/apiClient';

export default function DocumentsPage({ showToast, setModalState }) {
  const { businessTemplateBundle, backendProfileId } = useBusinessAnalysis();
  const { activeBusiness } = useAuth();
  const { documentsList: initialDocumentsList } = businessTemplateBundle;

  const [documents, setDocuments] = useState(initialDocumentsList);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');

  // Reactively sync documents whenever active business workspace or category changes
  useEffect(() => {
    let isMounted = true;
    const baseDocs = businessTemplateBundle?.documentsList || [];
    const targetProfileId = activeBusiness?.id || backendProfileId;

    async function loadBusinessDocuments() {
      if (targetProfileId) {
        try {
          const backendDocs = await apiClient.getDocuments({ business_profile_id: targetProfileId });
          if (isMounted && Array.isArray(backendDocs) && backendDocs.length > 0) {
            // Merge backend uploaded documents with baseline required documents
            const backendDocNames = new Set(backendDocs.map((d) => d.name.toLowerCase()));
            const remainingBaseDocs = baseDocs.filter((d) => !backendDocNames.has(d.name.toLowerCase()));
            setDocuments([...backendDocs, ...remainingBaseDocs]);
            return;
          }
        } catch {
          // Backend offline or fallback to template workspace
        }
      }
      if (isMounted) {
        setDocuments(baseDocs);
      }
    }

    loadBusinessDocuments();

    return () => {
      isMounted = false;
    };
  }, [activeBusiness?.id, businessTemplateBundle, backendProfileId]);

  const categories = ['All', ...new Set(documents.map((d) => d.category))];
  const statuses = ['All', 'Verified', 'Pending', 'Rejected'];

  const filteredDocs = documents.filter((doc) => {
    const matchSearch = doc.name.toLowerCase().includes(search.toLowerCase()) ||
      ((doc.mapped_approval || doc.relatedApproval) && (doc.mapped_approval || doc.relatedApproval).toLowerCase().includes(search.toLowerCase())) ||
      doc.category.toLowerCase().includes(search.toLowerCase());
    const matchCat = categoryFilter === 'All' || doc.category === categoryFilter;
    const matchStatus = statusFilter === 'All' || doc.status === statusFilter;
    return matchSearch && matchCat && matchStatus;
  });

  const handleOpenUpload = () => {
    setModalState({
      isOpen: true,
      title: 'Upload Business Document',
      type: 'upload-document',
      data: {
        businessProfileId: activeBusiness?.id || backendProfileId,
        approvalsList: businessTemplateBundle?.approvalsList || [],
        onUpload: (newDoc) => {
          setDocuments((prev) => [newDoc, ...prev.filter((d) => d.name.toLowerCase() !== newDoc.name.toLowerCase())]);
          if (showToast) showToast(`Document "${newDoc.name}" uploaded successfully.`);
        },
      },
    });
  };

  const handleOpenDetail = (doc) => {
    setModalState({
      isOpen: true,
      title: doc.name,
      type: 'document-detail',
      data: {
        ...doc,
        onDelete: (deletedId) => {
          setDocuments((prev) => prev.filter((d) => d.id !== deletedId));
        },
      },
    });
  };

  const totalDocsCount = documents.length;
  const verifiedDocsCount = documents.filter((d) => d.status === 'Verified' || d.evidence_status === 'Supported').length;
  const pendingDocsCount = documents.filter((d) => d.status === 'Pending' || d.status === 'Uploaded' || d.evidence_status === 'Needs Review').length;
  const expiringDocsCount = documents.filter((d) => d.status === 'Rejected' || d.expiry_radar === 'Expired' || d.expiry_radar === 'Critical').length;
  const coveragePercent = totalDocsCount > 0 ? Math.round((verifiedDocsCount / totalDocsCount) * 100) : 100;

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-1">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Documents Vault
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
            Securely manage and track all business statutory licenses and compliance filings.
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          onClick={handleOpenUpload}
          className="self-start sm:self-auto text-xs font-semibold"
        >
          <UploadCloud className="w-3.5 h-3.5" />
          <span>Upload Document</span>
        </Button>
      </div>

      {/* Top 4 Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5 sm:gap-5">
        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-400">Total Documents</div>
            <div className="text-xl sm:text-2xl font-black text-white mt-1">{totalDocsCount}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Digital vault</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-950/80 text-blue-400 flex items-center justify-center border border-blue-800/80 shrink-0">
            <FolderKanban className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-400">Verified</div>
            <div className="text-xl sm:text-2xl font-black text-emerald-400 mt-1">{verifiedDocsCount}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Authority approved</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-950/80 text-emerald-400 flex items-center justify-center border border-emerald-800/80 shrink-0">
            <FileCheck className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-400">Pending Review</div>
            <div className="text-xl sm:text-2xl font-black text-amber-400 mt-1">{pendingDocsCount}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Under audit / verification</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-amber-950/80 text-amber-400 flex items-center justify-center border border-amber-800/80 shrink-0">
            <Clock className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-400">Expiring Soon</div>
            <div className="text-xl sm:text-2xl font-black text-rose-400 mt-1">{expiringDocsCount}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Renewal required</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-rose-950/80 text-rose-400 flex items-center justify-center border border-rose-800/80 shrink-0">
            <XCircle className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* STATUTORY EVIDENCE COVERAGE MATRIX */}
      <div className="bg-[#111827] rounded-2xl border border-blue-900/50 p-4 sm:p-5 shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-blue-950/80 text-blue-400 border border-blue-800 flex items-center justify-center shrink-0">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-white tracking-wide">Statutory Evidence Coverage</h3>
                <span className="text-[10px] font-black uppercase px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                  {coveragePercent}% COVERED
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Document intelligence extracts regulatory identifiers and binds files directly to mandatory licenses.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0 text-xs font-semibold">
            <span className="px-2.5 py-1 rounded-lg bg-emerald-950/80 text-emerald-400 border border-emerald-800/80">
              {verifiedDocsCount} Supported
            </span>
            <span className="px-2.5 py-1 rounded-lg bg-amber-950/80 text-amber-400 border border-amber-800/80">
              {pendingDocsCount} Under Review
            </span>
            <span className="px-2.5 py-1 rounded-lg bg-rose-950/80 text-rose-400 border border-rose-800/80">
              {expiringDocsCount} Expired / Flagged
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-3 text-xs">
          <div className="p-2.5 rounded-xl bg-[#141C2B] border border-slate-800">
            <span className="text-[11px] text-slate-400 block">Identity &amp; Constitution Evidence</span>
            <span className="font-semibold text-slate-200 mt-0.5 block">PAN, Udyam Registration, Partnership Deed</span>
            <span className="text-[10px] text-emerald-400 mt-1 font-mono font-bold block">100% Verified</span>
          </div>
          <div className="p-2.5 rounded-xl bg-[#141C2B] border border-slate-800">
            <span className="text-[11px] text-slate-400 block">Premises &amp; Safety Proofs</span>
            <span className="font-semibold text-slate-200 mt-0.5 block">Property Tax Challan, Fire NOC, EB Bill</span>
            <span className="text-[10px] text-amber-400 mt-1 font-mono font-bold block">Renewal Due (15 Jun)</span>
          </div>
          <div className="p-2.5 rounded-xl bg-[#141C2B] border border-slate-800">
            <span className="text-[11px] text-slate-400 block">Environmental &amp; Factory Permits</span>
            <span className="font-semibold text-slate-200 mt-0.5 block">TNPCB Consent (CTO), Factory Building Plan</span>
            <span className="text-[10px] text-blue-400 mt-1 font-mono font-bold block">Active &amp; Mapped</span>
          </div>
        </div>
      </div>
      <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div className="flex-1 max-w-sm">
          <SearchInput
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onClear={() => setSearch('')}
            placeholder="Search documents, categories..."
          />
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
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

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 text-xs font-medium rounded-xl border border-[#1E293B] bg-[#141C2B] hover:border-slate-700 focus:border-blue-500 focus:outline-none transition-all text-slate-200"
          >
            {statuses.map((s) => (
              <option key={s} value={s}>
                Status: {s}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Documents Table */}
      {filteredDocs.length === 0 ? (
        <EmptyState
          title="No documents found"
          description="Adjust your search filters or click Upload Document to add files to your vault."
          actionLabel="Clear Filters"
          onAction={() => {
            setSearch('');
            setCategoryFilter('All');
            setStatusFilter('All');
          }}
        />
      ) : (
        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs overflow-hidden">
          {/* Desktop Table View */}
          <div className="hidden md:block overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider text-[11px] bg-[#141C2B]/50">
                  <th className="py-3.5 px-4">Document Name</th>
                  <th className="py-3.5 px-4">Category</th>
                  <th className="py-3.5 px-4">Related Approval</th>
                  <th className="py-3.5 px-4">Uploaded</th>
                  <th className="py-3.5 px-4">Expiry Date</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-medium text-slate-300">
                {filteredDocs.map((doc) => (
                  <tr key={doc.id} className="hover:bg-[#141C2B]/60 transition-colors group">
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-blue-950 text-blue-400 flex items-center justify-center font-bold text-[10px] border border-blue-800 shrink-0">
                          {doc.fileType || 'PDF'}
                        </div>
                        <div>
                          <div className="font-bold text-white group-hover:text-blue-400 transition-colors">
                            {doc.name}
                          </div>
                          <span className="text-[11px] text-slate-400">{doc.fileSize}</span>
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-slate-400">{doc.category}</td>
                    <td className="py-4 px-4 text-slate-200 font-medium">{doc.relatedApproval}</td>
                    <td className="py-4 px-4 text-slate-400">{doc.uploadDate}</td>
                    <td className="py-4 px-4 text-slate-400">{doc.expiryDate}</td>
                    <td className="py-4 px-4">
                      <Badge variant={doc.status} withDot>
                        {doc.status}
                      </Badge>
                    </td>
                    <td className="py-4 px-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => handleOpenDetail(doc)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
                          title="Preview Document"
                          aria-label="Preview Document"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={async () => {
                            if (doc.storage_path) {
                              try {
                                await apiClient.downloadDocumentFile(doc.id, doc.file_name || `${doc.name}.${(doc.file_type || 'pdf').toLowerCase()}`);
                                if (showToast) showToast(`Downloaded "${doc.name}" successfully.`);
                              } catch {
                                if (showToast) showToast('Download failed. Document service might be unreachable.');
                              }
                            } else {
                              if (showToast) showToast(`Downloading statutory verification reference for "${doc.name}"...`);
                            }
                          }}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
                          title="Download File"
                          aria-label="Download File"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile Card View */}
          <div className="md:hidden divide-y divide-slate-800/60">
            {filteredDocs.map((doc) => (
              <div key={doc.id} className="p-4 space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2.5">
                    <span className="w-7 h-7 rounded-md bg-blue-950 text-blue-400 flex items-center justify-center font-bold text-[10px] border border-blue-800">
                      {doc.fileType || doc.file_type || 'PDF'}
                    </span>
                    <div>
                      <h3 className="font-bold text-white text-xs">{doc.name}</h3>
                      <span className="text-[10px] text-slate-400">
                        {doc.fileSize || doc.file_size || 'Standard Size'} • {doc.category}
                      </span>
                    </div>
                  </div>
                  <Badge variant={doc.status} withDot size="xs">
                    {doc.status}
                  </Badge>
                </div>

                <div className="text-xs text-slate-300 bg-[#141C2B] p-2.5 rounded-xl border border-slate-800 space-y-1">
                  <div><strong>Approval:</strong> {doc.mapped_approval || doc.relatedApproval}</div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span>Uploaded: {doc.upload_date || doc.uploadDate}</span>
                    <span>Expiry: {doc.expiry_date || doc.expiryDate}</span>
                  </div>
                </div>

                <div className="flex items-center justify-end gap-2 pt-1">
                  <button
                    onClick={() => handleOpenDetail(doc)}
                    className="px-3 py-1.5 rounded-lg bg-blue-950 text-blue-400 text-xs font-semibold hover:bg-blue-900 border border-blue-800 cursor-pointer"
                  >
                    View Details
                  </button>
                  <button
                    onClick={async () => {
                      if (doc.storage_path) {
                        try {
                          await apiClient.downloadDocumentFile(doc.id, doc.file_name || `${doc.name}.${(doc.file_type || 'pdf').toLowerCase()}`);
                          if (showToast) showToast(`Downloaded "${doc.name}" successfully.`);
                        } catch {
                          if (showToast) showToast('Download failed.');
                        }
                      } else {
                        if (showToast) showToast(`Downloading statutory record for "${doc.name}"...`);
                      }
                    }}
                    className="px-3 py-1.5 rounded-lg bg-[#141C2B] text-slate-300 text-xs font-semibold hover:bg-slate-800 border border-slate-700 cursor-pointer"
                  >
                    Download
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}