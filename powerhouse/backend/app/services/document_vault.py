import os
import re
import hashlib
from typing import Tuple, Optional
from fastapi import HTTPException, status as http_status

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx"}
MAGIC_SIGNATURES = {
    ".pdf": [b"%PDF-"],
    ".docx": [b"PK\x03\x04"],
    ".xlsx": [b"PK\x03\x04"],
}


class DocumentVaultService:
    @staticmethod
    def get_upload_dir() -> str:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        return UPLOAD_DIR

    @staticmethod
    def validate_file(file_bytes: bytes, filename: str, content_type: Optional[str] = None) -> Tuple[str, str, str]:
        """
        Validates file existence, size, extension, and magic bytes.
        Returns (extension, formatted_size, sha256_hash).
        """
        if not file_bytes or len(file_bytes) == 0:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No file selected or file is empty.",
            )

        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=http_status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File exceeds the 25 MB limit.",
            )

        _, ext = os.path.splitext(filename or "")
        ext = ext.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=http_status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"This file type is not supported. Supported formats: PDF, DOCX, XLSX.",
            )

        # Magic byte signature check
        expected_magics = MAGIC_SIGNATURES.get(ext, [])
        matched = any(file_bytes.startswith(sig) for sig in expected_magics)
        if not matched:
            raise HTTPException(
                status_code=http_status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="File content signature does not match its extension. Corrupted or invalid file.",
            )

        # Calculate file size label
        size_bytes = len(file_bytes)
        if size_bytes >= 1024 * 1024:
            size_label = f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            size_label = f"{size_bytes / 1024:.0f} KB"

        content_hash = hashlib.sha256(file_bytes).hexdigest()
        file_type = ext.replace(".", "").upper()

        return file_type, size_label, content_hash

    @staticmethod
    def store_file(business_profile_id: str, doc_id: str, original_filename: str, file_bytes: bytes) -> str:
        """
        Stores file safely in isolated business directory.
        Protects against path traversal attacks.
        """
        # Sanitize filename
        safe_name = os.path.basename(original_filename)
        safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", safe_name)
        if not safe_name:
            safe_name = f"document_{doc_id}.pdf"

        tenant_dir = os.path.join(DocumentVaultService.get_upload_dir(), str(business_profile_id))
        os.makedirs(tenant_dir, exist_ok=True)

        stored_filename = f"{doc_id}_{safe_name}"
        full_path = os.path.join(tenant_dir, stored_filename)

        with open(full_path, "wb") as f:
            f.write(file_bytes)

        return full_path

    @staticmethod
    def delete_stored_file(storage_path: Optional[str]):
        """Safely cleans up orphaned file if DB transaction fails."""
        if not storage_path:
            return
        try:
            if os.path.exists(storage_path):
                os.remove(storage_path)
        except Exception:
            pass

    @staticmethod
    def get_verified_path(storage_path: str) -> str:
        """
        Ensures storage path is canonical, within UPLOAD_DIR, and exists.
        """
        if not storage_path:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="File path is empty or not registered.",
            )

        canon_upload = os.path.realpath(DocumentVaultService.get_upload_dir())
        canon_target = os.path.realpath(storage_path)

        if not canon_target.startswith(canon_upload):
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: illegal path traversal detected.",
            )

        if not os.path.exists(canon_target):
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Document file not found on disk.",
            )

        return canon_target
