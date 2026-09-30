import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base


class RegulatoryKnowledgeDocument(Base):
    """
    Authoritative Regulatory Knowledge Document model.
    Only documents with verification_status in ['VERIFIED', 'ACTIVE'] may be cited
    as supporting regulatory evidence.
    """
    __tablename__ = 'regulatory_knowledge_documents'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    source_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    authority = Column(String(255), nullable=False)
    jurisdiction = Column(String(100), nullable=False)  # Central, State (Tamil Nadu), Municipal, etc.
    document_type = Column(String(100), nullable=False)  # Act, Rules, Regulation, Circular, Gazette Notification
    act_name = Column(String(255), nullable=False)
    section = Column(String(100), nullable=True)
    category = Column(String(100), nullable=False, index=True)  # restaurant, clothing_textile, jewellery, retail, manufacturing, general_statutory
    effective_date = Column(String(100), nullable=True)
    verification_status = Column(String(50), nullable=False, default='VERIFIED', index=True)  # INGESTED, REVIEWED, VERIFIED, ACTIVE, RETIRED
    version = Column(Integer, nullable=False, default=1)
    source_url = Column(String(500), nullable=True)
    content_hash = Column(String(64), nullable=False)  # SHA-256 hash for deduplication
    raw_text = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    chunks = relationship('RegulatoryChunk', back_populates='document', cascade='all, delete-orphan')


class RegulatoryChunk(Base):
    """
    Statutory-aware chunk with complete provenance and legal hierarchy.
    """
    __tablename__ = 'regulatory_chunks'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    document_id = Column(String(36), ForeignKey('regulatory_knowledge_documents.id', ondelete='CASCADE'), nullable=False, index=True)
    source_id = Column(String(100), nullable=False, index=True)
    chunk_id = Column(String(120), unique=True, nullable=False, index=True)

    chapter = Column(String(100), nullable=True)
    section = Column(String(100), nullable=True)
    subsection = Column(String(100), nullable=True)
    rule = Column(String(100), nullable=True)

    content = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False)
    jurisdiction = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    verification_status = Column(String(50), nullable=False, default='VERIFIED', index=True)
    embedding_id = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship('RegulatoryKnowledgeDocument', back_populates='chunks')
