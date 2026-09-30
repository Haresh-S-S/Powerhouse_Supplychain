import os
import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status as http_status,
    Query,
    UploadFile,
    File,
    Form,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_optional_user
from app.models.user import User
from app.models.business import BusinessProfile
from app.models.approval import Approval
from app.models.document import Document
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
)
from app.services.document_service import DocumentService
from app.services.document_vault import DocumentVaultService
from app.services.document_intelligence import DocumentIntelligenceService
from app.rag.vector_store import get_vector_store

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=List[DocumentResponse])
def list_documents(
    business_profile_id: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    if business_profile_id:
        profile = db.query(BusinessProfile).filter(BusinessProfile.id == business_profile_id).first()
        if not profile:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Business profile '{business_profile_id}' not found.",
            )
        if current_user and profile.user_id and profile.user_id != current_user.id:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you do not have permission to view documents for this business.",
            )
        return DocumentService.list_documents(
            db,
            business_profile_id=business_profile_id,
            category=category,
            status=status,
            skip=skip,
            limit=limit,
        )

    # If no profile specified, but user is authenticated, show all docs across user's profiles
    if current_user:
        user_profiles = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).all()
        profile_ids = [p.id for p in user_profiles]
        query = db.query(Document).filter(Document.business_profile_id.in_(profile_ids))
        if category:
            query = query.filter(Document.category == category)
        if status:
            query = query.filter(Document.status == status)
        docs = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
        for d in docs:
            DocumentService.enrich_document_response(db, d)
        return docs

    return DocumentService.list_documents(
        db,
        business_profile_id=None,
        category=category,
        status=status,
        skip=skip,
        limit=limit,
    )


@router.post("/upload", response_model=DocumentResponse, status_code=http_status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    business_profile_id: str = Form(...),
    title: str = Form(...),
    category: str = Form("Statutory License"),
    related_approval: Optional[str] = Form(None),
    approval_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Complete end-to-end document upload:
    1. Authentication and business ownership check.
    2. File format, size (<=25MB), and magic byte validation.
    3. Transaction-safe storage in secure vault.
    4. Database record creation with duplicate detection.
    5. Document Intelligence analysis (with failure isolation).
    """
    # 1. Validate required title
    if not title or not title.strip():
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Enter a document title.",
        )

    clean_title = title.strip()

    # 2. Check business profile ownership
    profile = db.query(BusinessProfile).filter(BusinessProfile.id == business_profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Business profile '{business_profile_id}' not found.",
        )

    if current_user and profile.user_id and profile.user_id != current_user.id:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not have permission to upload documents for this business profile.",
        )

    # 3. Read and validate file content
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to read uploaded file: {str(e)}",
        )

    file_type, size_label, content_hash = DocumentVaultService.validate_file(
        file_bytes=file_bytes,
        filename=file.filename or "upload.pdf",
        content_type=file.content_type,
    )

    # 4. Check for duplicate upload
    existing = DocumentService.get_by_hash(db, business_profile_id, content_hash)
    if existing:
        return existing

    # 5. Store file securely
    doc_id = str(uuid.uuid4())
    storage_path = None
    try:
        storage_path = DocumentVaultService.store_file(
            business_profile_id=business_profile_id,
            doc_id=doc_id,
            original_filename=file.filename or f"doc_{doc_id}.pdf",
            file_bytes=file_bytes,
        )

        now_str = datetime.now().strftime("%d %b %Y")
        
        # Determine approval ID link
        linked_approval_id = approval_id
        if not linked_approval_id and related_approval and related_approval != "Not linked yet":
            appr = db.query(Approval).filter(
                Approval.business_profile_id == business_profile_id,
                Approval.name == related_approval
            ).first()
            if appr:
                linked_approval_id = appr.id

        # 6. Database record creation
        new_doc = Document(
            id=doc_id,
            business_profile_id=business_profile_id,
            approval_id=linked_approval_id,
            name=clean_title,
            category=category,
            file_name=file.filename or f"{clean_title}.{file_type.lower()}",
            file_type=file_type,
            file_size=size_label,
            status="Uploaded",
            required=True,
            upload_date=now_str,
            expiry_date="Perpetual",
            verification_date=now_str,
            renewal_cycle="Annual",
            storage_path=storage_path,
            content_hash=content_hash,
            analysis_status="Uploaded",
            extracted_data=None,
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)

    except Exception as db_err:
        # Transaction safety: remove stored file if DB commit fails
        DocumentVaultService.delete_stored_file(storage_path)
        db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document upload could not be completed due to database error. Please try again.",
        )

    # 7. Run Document Intelligence (Separate Failure Domain)
    business_approvals = db.query(Approval).filter(Approval.business_profile_id == business_profile_id).all()
    tenant_id = profile.user_id or "tenant-default"

    try:
        intel_result = DocumentIntelligenceService.analyze_and_index_document(
            tenant_id=tenant_id,
            business_profile_id=business_profile_id,
            document_id=doc_id,
            doc_name=clean_title,
            category=category,
            file_path=storage_path,
            file_type=file_type,
            related_approval=related_approval,
            business_approvals=business_approvals,
        )

        new_doc.analysis_status = "Analyzed"
        new_doc.status = "Verified" if intel_result.get("evidence_status") == "Supported" else "Needs Review"
        new_doc.expiry_date = intel_result.get("expiry_date", new_doc.expiry_date)
        new_doc.extracted_data = json.dumps(intel_result)
        db.commit()
        db.refresh(new_doc)

    except Exception as intel_err:
        # Document remains safely stored even if intelligence analysis fails!
        new_doc.analysis_status = "Failed"
        new_doc.status = "Needs Review"
        new_doc.extracted_data = json.dumps({
            "error": "Intelligence analysis unavailable.",
            "evidence_status": "Needs Review",
            "mapped_approval": related_approval or "General Statutory Compliance",
        })
        db.commit()
        db.refresh(new_doc)

    DocumentService.enrich_document_response(db, new_doc)
    return new_doc


@router.post("", response_model=DocumentResponse, status_code=http_status.HTTP_201_CREATED)
def create_document(
    schema: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    if current_user and schema.business_profile_id:
        profile = db.query(BusinessProfile).filter(BusinessProfile.id == schema.business_profile_id).first()
        if profile and profile.user_id and profile.user_id != current_user.id:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you do not have permission to upload documents for this profile.",
            )
    return DocumentService.create_document(db, schema)


@router.get("/{id}", response_model=DocumentResponse)
def get_document(
    id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    doc = DocumentService.get_document(db, id)
    if not doc:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Document with id '{id}' not found",
        )
    if current_user and doc.business_profile and doc.business_profile.user_id:
        if doc.business_profile.user_id != current_user.id:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you do not have permission to view this document.",
            )
    return doc


@router.get("/{id}/file")
def download_document_file(
    id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Secure file streaming with tenant ownership verification and path traversal guard.
    """
    doc = DocumentService.get_document(db, id)
    if not doc:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Document with id '{id}' not found",
        )
    if current_user and doc.business_profile and doc.business_profile.user_id:
        if doc.business_profile.user_id != current_user.id:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you do not have permission to access this document file.",
            )

    safe_path = DocumentVaultService.get_verified_path(doc.storage_path)

    media_type = "application/pdf" if doc.file_type == "PDF" else "application/octet-stream"
    return FileResponse(
        path=safe_path,
        filename=doc.file_name or f"{doc.name}.{doc.file_type.lower()}",
        media_type=media_type,
    )


@router.get("/{id}/intelligence")
def get_document_intelligence(
    id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Returns document intelligence, extracted statutory identifiers, expiry radar,
    and evidence coverage status.
    """
    doc = DocumentService.get_document(db, id)
    if not doc:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Document with id '{id}' not found",
        )
    if current_user and doc.business_profile and doc.business_profile.user_id:
        if doc.business_profile.user_id != current_user.id:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you do not have permission to view this document intelligence.",
            )

    intel = {}
    if doc.extracted_data:
        try:
            intel = json.loads(doc.extracted_data)
        except Exception:
            intel = {}

    return {
        "document_id": doc.id,
        "name": doc.name,
        "category": doc.category,
        "file_name": doc.file_name,
        "file_type": doc.file_type,
        "file_size": doc.file_size,
        "status": doc.status,
        "analysis_status": doc.analysis_status,
        "mapped_approval": getattr(doc, "mapped_approval", "General Statutory Compliance"),
        "evidence_status": getattr(doc, "evidence_status", "Supported"),
        "upload_date": doc.upload_date,
        "expiry_date": doc.expiry_date,
        "intelligence": intel,
    }


@router.patch("/{id}", response_model=DocumentResponse)
def update_document(
    id: str,
    schema: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    doc = DocumentService.get_document(db, id)
    if not doc:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Document with id '{id}' not found",
        )
    if current_user and doc.business_profile and doc.business_profile.user_id:
        if doc.business_profile.user_id != current_user.id:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you do not have permission to modify this document.",
            )
    return DocumentService.update_document(db, id, schema)


@router.delete("/{id}", status_code=http_status.HTTP_200_OK)
def delete_document(
    id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    doc = DocumentService.get_document(db, id)
    if not doc:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Document with id '{id}' not found",
        )
    if current_user and doc.business_profile and doc.business_profile.user_id:
        if doc.business_profile.user_id != current_user.id:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you do not have permission to delete this document.",
            )

    # Clean up file from disk
    DocumentVaultService.delete_stored_file(doc.storage_path)

    # Clean up vector index in ChromaDB
    try:
        vs = get_vector_store()
        tenant_id = doc.business_profile.user_id if doc.business_profile else "tenant-default"
        vs.delete_business_document(
            tenant_id=tenant_id,
            business_profile_id=doc.business_profile_id,
            document_id=doc.id
        )
    except Exception:
        pass

    DocumentService.delete_document(db, id)
    return {"message": "Document deleted successfully", "id": id}
