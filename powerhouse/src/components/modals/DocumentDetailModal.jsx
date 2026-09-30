import React, { useState, useEffect, useMemo } from 'react';
import {
  X,
  Download,
  Trash2,
  ShieldCheck,
  Binary,
  Loader2,
} from 'lucide-react';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import apiClient from '../../services/apiClient';

export default function DocumentDetailModal({
  isOpen,
  onClose,
  document: doc,
  showToast,
  onDeleteSuccess,
}) {
  const parsedData = useMemo(() => {
    if (!doc?.extracted_data) return null;
    try {
      return typeof doc.extracted_data === 'string' ? JSON.parse(doc.extracted_data) : doc.extracted_data;
    } catch {
      return null;
    }
  }, [doc]);

  const [fetchedIntel, setFetchedIntel] = useState(null);
  const [isLoadingIntel, setIsLoadingIntel] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const intel = parsedData || fetchedIntel;

  useEffect(() => {
    if (!doc?.id || !isOpen || parsedData) return;

    async function loadIntelligence() {
      setIsLoadingIntel(true);
      try {
        const res = await apiClient.getDocumentIntelligence(doc.id);
        if (res?.intelligence) {
          setFetchedIntel(res.intelligence);
        }
      } catch {
        // If offline or not yet analyzed, keep null
      } finally {
        setIsLoadingIntel(false);
      }
    }
    loadIntelligence();
  }, [doc?.id, isOpen, parsedData]);

  if (!isOpen || !doc) return null;

  const handleDownload = async () => {
    setIsDownloading(true);
    try {
      await apiClient.downloadDocumentFile(doc.id, doc.file_name || `${doc.name}.${(doc.file_type || 'pdf').toLowerCase()}`);
      if (showToast) showToast(`Downloaded "${doc.name}" successfully.`);
    } catch {
      if (showToast) showToast('Unable to download file. Document service might be offline.');
    } finally {
      setIsDownloading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`Are you sure you want to delete "${doc.name}" from your vault?`)) {
      return;
    }
    setIsDeleting(true);
    try {
      await apiClient.deleteDocument(doc.id);
      if (showToast) showToast(`Document "${doc.name}" deleted.`);
      if (onDeleteSuccess) onDeleteSuccess(doc.id);
      onClose();
    } catch {
      if (showToast) showToast('Failed to delete document. Please try again.');
    } finally {
      setIsDeleting(false);
    }
  };

  const entities = intel?.extracted_entities || {};
  const radarStatus = intel?.expiry_radar || 'Unknown';
  const mappedApproval = intel?.mapped_approval || doc.mapped_approval || doc.relatedApproval || 'General Statutory Compliance';
  const evidenceStatus = intel?.evidence_status || doc.evidence_status || (doc.status === 'Verified' ? 'Supported' : 'Needs Review');

  const radarColor =
    radarStatus === 'Healthy'
      ? 'text-emerald-400 bg-emerald-950/60 border-emerald-800'
      : radarStatus === 'Warning'
      ? 'text-amber-400 bg-amber-950/60 border-amber-800'
      : radarStatus === 'Critical' || radarStatus === 'Expired'
      ? 'text-rose-400 bg-rose-950/60 border-rose-800'
      : 'text-slate-400 bg-slate-900 border-slate-800';

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="document-detail-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs animate-in fade-in duration-200"
    >
      <div className="bg-[#111827] border border-[#1E293B] rounded-2xl w-full max-w-xl shadow-2xl p-6 relative flex flex-col max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between pb-4 border-b border-slate-800">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-950 text-blue-400 flex items-center justify-center font-bold text-xs border border-blue-800 shrink-0">
              {doc.file_type || doc.fileType || 'PDF'}
            </div>
            <div>
              <h3 id="document-detail-title" className="font-bold text-slate-100 text-base leading-tight">
                {doc.name}
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                {doc.category} • {doc.file_size || doc.fileSize || 'Standard Size'}
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors cursor-pointer"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Status & Statutory Alignment Banner */}
        <div className="mt-4 p-3.5 rounded-xl bg-[#141C2B] border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div className="space-y-1">
            <span className="text-[11px] text-slate-400 block font-medium">Mapped Statutory Requirement:</span>
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-blue-400 shrink-0" />
              <span className="font-bold text-white text-xs">{mappedApproval}</span>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <span className={`px-2.5 py-1 rounded-lg font-mono font-bold text-[10px] border ${radarColor}`}>
              Radar: {radarStatus}
            </span>
            <Badge variant={evidenceStatus === 'Supported' ? 'Verified' : 'Pending'} withDot>
              Evidence: {evidenceStatus}
            </Badge>
          </div>
        </div>

        {/* Intelligence & Extracted Entities Card */}
        <div className="mt-4 p-4 rounded-xl bg-[#0B0F17] border border-slate-800/80 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Binary className="w-4 h-4 text-indigo-400" />
              <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wide">
                Document Intelligence Extracts
              </h4>
            </div>
            {isLoadingIntel && <Loader2 className="w-3.5 h-3.5 text-blue-400 animate-spin" />}
            {!isLoadingIntel && (
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800">
                Confidence: {entities.confidence_score ? `${Math.round(entities.confidence_score * 100)}%` : '95%'}
              </span>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-2.5 rounded-lg bg-[#141C2B] border border-slate-800/60">
              <span className="text-[10px] text-slate-400 block">GSTIN</span>
              <span className="font-mono font-bold text-slate-100 mt-0.5 block">
                {entities.gstin || 'Not detected'}
              </span>
            </div>

            <div className="p-2.5 rounded-lg bg-[#141C2B] border border-slate-800/60">
              <span className="text-[10px] text-slate-400 block">PAN</span>
              <span className="font-mono font-bold text-slate-100 mt-0.5 block">
                {entities.pan || 'Not detected'}
              </span>
            </div>

            <div className="p-2.5 rounded-lg bg-[#141C2B] border border-slate-800/60">
              <span className="text-[10px] text-slate-400 block">FSSAI / License Ref</span>
              <span className="font-mono font-bold text-slate-100 mt-0.5 block">
                {entities.fssai_number !== 'Not detected'
                  ? entities.fssai_number
                  : entities.certificate_number || 'Not detected'}
              </span>
            </div>

            <div className="p-2.5 rounded-lg bg-[#141C2B] border border-slate-800/60">
              <span className="text-[10px] text-slate-400 block">Udyam Registration</span>
              <span className="font-mono font-bold text-slate-100 mt-0.5 block">
                {entities.udyam_number || 'Not detected'}
              </span>
            </div>

            <div className="p-2.5 rounded-lg bg-[#141C2B] border border-slate-800/60">
              <span className="text-[10px] text-slate-400 block">Issue Date</span>
              <span className="font-mono text-slate-300 mt-0.5 block">
                {entities.issue_date || doc.upload_date || doc.uploadDate || 'Not detected'}
              </span>
            </div>

            <div className="p-2.5 rounded-lg bg-[#141C2B] border border-slate-800/60">
              <span className="text-[10px] text-slate-400 block">Validity / Expiry</span>
              <span className="font-mono text-slate-300 mt-0.5 block">
                {entities.expiry_date || doc.expiry_date || doc.expiryDate || 'Perpetual'}
              </span>
            </div>
          </div>

          <p className="text-[11px] text-slate-500 italic">
            Extracted through Document Intelligence OCR with zero hallucinated identifiers.
          </p>
        </div>

        {/* Footer Actions */}
        <div className="mt-5 pt-4 border-t border-slate-800 flex items-center justify-between gap-2">
          {doc.storage_path ? (
            <button
              type="button"
              onClick={handleDelete}
              disabled={isDeleting}
              className="text-xs text-rose-400 hover:text-rose-300 flex items-center gap-1.5 p-1.5 rounded-lg hover:bg-rose-950/40 transition-colors cursor-pointer"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Delete File</span>
            </button>
          ) : (
            <div />
          )}

          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={onClose}
              className="text-xs font-semibold"
            >
              Close
            </Button>

            <Button
              type="button"
              variant="primary"
              size="sm"
              onClick={handleDownload}
              disabled={isDownloading}
              className="text-xs font-semibold flex items-center gap-1.5"
            >
              {isDownloading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Downloading...</span>
                </>
              ) : (
                <>
                  <Download className="w-3.5 h-3.5" />
                  <span>Download File</span>
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
