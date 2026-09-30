import React, { useState, useRef } from 'react';
import { UploadCloud, X, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import Button from '../ui/Button';
import apiClient from '../../services/apiClient';

const MAX_FILE_SIZE = 25 * 1024 * 1024; // 25 MB
const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.xlsx'];

const CATEGORY_OPTIONS = [
  'Statutory License',
  'Environmental',
  'Safety',
  'Taxation',
  'Financial Compliance',
  'Certification',
  'Labour & Employment',
];

export default function UploadDocumentModal({
  isOpen,
  onClose,
  businessProfileId,
  approvalsList = [],
  onUploadSuccess,
  showToast,
}) {
  const [file, setFile] = useState(null);
  const [docTitle, setDocTitle] = useState('');
  const [category, setCategory] = useState('Statutory License');
  const [relatedApproval, setRelatedApproval] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const fileInputRef = useRef(null);

  if (!isOpen) return null;

  // Build business-specific approvals list + 'Not linked yet'
  const approvalOptions = [
    'Not linked yet',
    ...approvalsList.map((a) => (typeof a === 'string' ? a : a.name)).filter(Boolean),
  ];

  const effectiveApproval = relatedApproval || approvalOptions[0];

  const handleFileValidation = (selectedFile) => {
    setErrorMessage(null);

    if (!selectedFile) {
      setErrorMessage('No file selected.');
      return false;
    }

    const name = selectedFile.name || '';
    const ext = name.slice(name.lastIndexOf('.')).toLowerCase();

    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      setErrorMessage('This file type is not supported. Supported formats: PDF, DOCX, XLSX.');
      return false;
    }

    if (selectedFile.size > MAX_FILE_SIZE) {
      setErrorMessage('File exceeds the 25 MB limit.');
      return false;
    }

    setFile(selectedFile);
    // Autofill title if empty
    if (!docTitle) {
      const cleanName = name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' ');
      setDocTitle(cleanName);
    }
    return true;
  };

  const handleInputChange = (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileValidation(files[0]);
    }
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer?.files;
    if (files && files.length > 0) {
      handleFileValidation(files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!file) {
      setErrorMessage('No file selected. Please select a file to upload.');
      return;
    }

    if (!docTitle || !docTitle.trim()) {
      setErrorMessage('Enter a document title.');
      return;
    }

    if (!businessProfileId) {
      setErrorMessage('No active business workspace selected. Please select a business.');
      return;
    }

    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('business_profile_id', businessProfileId);
      formData.append('title', docTitle.trim());
      formData.append('category', category);
      formData.append('related_approval', effectiveApproval);

      const createdDoc = await apiClient.uploadDocument(formData);

      if (showToast) {
        showToast(`Document "${createdDoc.name}" uploaded successfully.`);
      }

      if (onUploadSuccess) {
        onUploadSuccess(createdDoc);
      }

      // Reset & Close
      setFile(null);
      setDocTitle('');
      setCategory('Statutory License');
      setRelatedApproval('');
      onClose();
    } catch (err) {
      let msg = 'Document upload could not be completed. Please try again.';

      if (err.isNetworkError) {
        msg = 'Document service is unavailable. Check your connection.';
      } else if (err.status === 401) {
        msg = 'Your session has expired. Please sign in again.';
      } else if (err.status === 403) {
        msg = 'You do not have access to this business document.';
      } else if (err.status === 413) {
        msg = 'File exceeds the 25 MB limit.';
      } else if (err.status === 415) {
        msg = 'This file type is not supported.';
      } else if (err.status === 422) {
        msg = err.message || 'Enter a document title.';
      } else if (err.message) {
        msg = err.message;
      }

      setErrorMessage(msg);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="upload-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs animate-in fade-in duration-200"
    >
      <div className="bg-[#111827] border border-[#1E293B] rounded-2xl w-full max-w-lg shadow-2xl p-6 relative flex flex-col max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div>
            <h3 id="upload-modal-title" className="font-bold text-slate-100 text-base">
              Upload Business Document
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Secure Document Vault with automatic entity extraction &amp; statutory evidence linkage.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={isUploading}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors cursor-pointer"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Error Alert */}
        {errorMessage && (
          <div className="mt-4 p-3 rounded-xl bg-rose-950/60 border border-rose-800 text-xs text-rose-300 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          {/* Upload Dropzone */}
          <div
            onClick={() => fileInputRef.current?.click()}
            onDragEnter={handleDragEnter}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-2xl p-6 text-center transition-all cursor-pointer ${
              isDragging
                ? 'border-blue-500 bg-blue-950/30 ring-2 ring-blue-500/20'
                : file
                ? 'border-emerald-700 bg-emerald-950/20'
                : 'border-slate-700 bg-[#141C2B] hover:bg-[#1e293b]/50'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.xlsx"
              onChange={handleInputChange}
              className="hidden"
            />

            {file ? (
              <div className="flex flex-col items-center gap-1.5">
                <CheckCircle2 className="w-8 h-8 text-emerald-400 mb-1" />
                <span className="text-xs font-bold text-slate-100">{file.name}</span>
                <span className="text-[11px] text-slate-400">
                  {(file.size / (1024 * 1024)).toFixed(2)} MB • Ready to upload
                </span>
                <span className="text-[10px] text-blue-400 underline mt-1">
                  Click or drop to replace file
                </span>
              </div>
            ) : (
              <>
                <UploadCloud className="w-8 h-8 text-blue-400 mx-auto mb-2" />
                <span className="text-xs font-bold text-slate-200 block">
                  Click to upload or drag &amp; drop
                </span>
                <span className="text-[11px] text-slate-500 block mt-0.5">
                  PDF, DOCX, XLSX up to 25MB
                </span>
              </>
            )}
          </div>

          {/* Document Title */}
          <div>
            <label className="block text-xs font-bold text-slate-300 mb-1">
              Document Title <span className="text-rose-400">*</span>
            </label>
            <input
              type="text"
              placeholder="e.g. Factory Licence Certificate"
              value={docTitle}
              onChange={(e) => setDocTitle(e.target.value)}
              className="w-full px-3 py-2 text-xs rounded-xl bg-[#141C2B] border border-[#1E293B] text-slate-100 placeholder-slate-500 focus:border-blue-500 focus:outline-none"
            />
          </div>

          {/* Category and Related License */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-300 mb-1">
                Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-xl bg-[#141C2B] border border-[#1E293B] text-slate-100 focus:border-blue-500 focus:outline-none"
              >
                {CATEGORY_OPTIONS.map((cat) => (
                  <option key={cat} value={cat} className="bg-[#111827]">
                    {cat}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-300 mb-1">
                Related License
              </label>
              <select
                value={effectiveApproval}
                onChange={(e) => setRelatedApproval(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-xl bg-[#141C2B] border border-[#1E293B] text-slate-100 focus:border-blue-500 focus:outline-none"
              >
                {approvalOptions.map((name) => (
                  <option key={name} value={name} className="bg-[#111827]">
                    {name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Footer Actions */}
          <div className="pt-4 border-t border-slate-800 flex justify-end gap-2">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={onClose}
              disabled={isUploading}
              className="text-xs font-semibold"
            >
              Close
            </Button>

            <Button
              type="submit"
              variant="primary"
              size="sm"
              disabled={!file || !docTitle.trim() || isUploading}
              className="text-xs font-semibold flex items-center gap-1.5"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Uploading...</span>
                </>
              ) : (
                <span>Upload File</span>
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
