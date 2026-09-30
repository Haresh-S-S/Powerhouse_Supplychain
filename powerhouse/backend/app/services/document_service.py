import json
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.approval import Approval
from app.schemas.document import DocumentCreate, DocumentUpdate


class DocumentService:
    @staticmethod
    def list_documents(
        db: Session,
        business_profile_id: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Document]:
        query = db.query(Document)
        if business_profile_id:
            query = query.filter(Document.business_profile_id == business_profile_id)
        if category:
            query = query.filter(Document.category == category)
        if status:
            query = query.filter(Document.status == status)
        docs = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
        for d in docs:
            DocumentService.enrich_document_response(db, d)
        return docs

    @staticmethod
    def get_document(db: Session, doc_id: str) -> Optional[Document]:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            DocumentService.enrich_document_response(db, doc)
        return doc

    @staticmethod
    def get_by_hash(db: Session, business_profile_id: str, content_hash: str) -> Optional[Document]:
        doc = db.query(Document).filter(
            Document.business_profile_id == business_profile_id,
            Document.content_hash == content_hash
        ).first()
        if doc:
            DocumentService.enrich_document_response(db, doc)
        return doc

    @staticmethod
    def create_document(db: Session, schema: DocumentCreate) -> Document:
        doc = Document(**schema.model_dump())
        db.add(doc)
        db.commit()
        db.refresh(doc)
        DocumentService.enrich_document_response(db, doc)
        return doc

    @staticmethod
    def update_document(db: Session, doc_id: str, schema: DocumentUpdate) -> Optional[Document]:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return None
        for key, value in schema.model_dump(exclude_unset=True).items():
            setattr(doc, key, value)
        db.commit()
        db.refresh(doc)
        DocumentService.enrich_document_response(db, doc)
        return doc

    @staticmethod
    def delete_document(db: Session, doc_id: str) -> bool:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return False
        db.delete(doc)
        db.commit()
        return True

    @staticmethod
    def enrich_document_response(db: Session, doc: Document) -> Document:
        """
        Enriches the Document model instance with mapped_approval and evidence_status
        for serialization into DocumentResponse.
        """
        mapped_approval = None
        evidence_status = "Supported" if doc.status == "Verified" else "Needs Review"

        # Check if extracted_data has mapped approval
        if doc.extracted_data:
            try:
                data = json.loads(doc.extracted_data)
                if isinstance(data, dict):
                    mapped_approval = data.get("mapped_approval")
                    if data.get("evidence_status"):
                        evidence_status = data.get("evidence_status")
            except Exception:
                pass

        if not mapped_approval and doc.approval_id:
            approval = db.query(Approval).filter(Approval.id == doc.approval_id).first()
            if approval:
                mapped_approval = approval.name
            else:
                mapped_approval = doc.approval_id

        if not mapped_approval:
            mapped_approval = "Not linked yet" if doc.status == "Pending" else "General Statutory Compliance"

        setattr(doc, "mapped_approval", mapped_approval)
        setattr(doc, "evidence_status", evidence_status)
        return doc
