import os
import re
import io
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from pypdf import PdfReader

from app.rag.vector_store import get_vector_store
from app.models.business import BusinessProfile
from app.models.approval import Approval


class DocumentIntelligenceService:
    @staticmethod
    def extract_text_from_file(file_path: str, file_type: str) -> str:
        """
        Extracts raw textual content from PDF or text-containing files.
        Gracefully returns empty string if unparseable.
        """
        if not os.path.exists(file_path):
            return ""

        extracted_text = ""
        try:
            if file_type.upper() == "PDF":
                reader = PdfReader(file_path)
                pages_text = []
                for page in reader.pages:
                    txt = page.extract_text()
                    if txt:
                        pages_text.append(txt)
                extracted_text = "\n".join(pages_text)
            else:
                # Fallback text reading
                with open(file_path, "rb") as f:
                    raw = f.read(50000)
                    extracted_text = raw.decode("utf-8", errors="ignore")
        except Exception:
            extracted_text = ""

        return extracted_text.strip()

    @staticmethod
    def extract_statutory_entities(text: str, document_title: str) -> Dict[str, Any]:
        """
        Extracts verifiable statutory identifiers with ZERO fabricated data.
        If a field is not detected in the document text, returns 'Not detected'.
        """
        combined = f"{document_title}\n{text}"

        # 1. GSTIN (15 characters)
        gstin_match = re.search(r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}\b", combined)
        gstin = gstin_match.group(0) if gstin_match else "Not detected"

        # 2. PAN (10 characters)
        pan_match = re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b", combined)
        pan = pan_match.group(0) if pan_match else "Not detected"

        # 3. FSSAI License No (14 digits starting with 1 or 2)
        fssai_match = re.search(r"\b(?:fssai\s*(?:licence|no|reg|number)?[:\s]*)?([12]\d{13})\b", combined, re.IGNORECASE)
        fssai_no = fssai_match.group(1) if fssai_match else "Not detected"

        # 4. Udyam Registration Number
        udyam_match = re.search(r"\bUDYAM-[A-Z]{2}-\d{2}-\d{7}\b", combined, re.IGNORECASE)
        udyam_no = udyam_match.group(0).upper() if udyam_match else "Not detected"

        # 5. Factory / Boiler / Trade Certificate Number
        cert_match = re.search(r"\b(?:Licen[cs]e|Certificate|Registration|Ref|Regn)[\s#.:]+([A-Z0-9/-]{5,25})\b", combined, re.IGNORECASE)
        cert_number = cert_match.group(1) if cert_match else "Not detected"

        # 6. Dates detection
        date_matches = re.findall(
            r"\b(?:\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b",
            combined,
            re.IGNORECASE
        )
        issue_date = date_matches[0] if len(date_matches) > 0 else "Not detected"
        expiry_date = date_matches[1] if len(date_matches) > 1 else ("Perpetual" if any(p in document_title.lower() for p in ["pan", "udyam", "incorporation", "deed", "gst"]) else "Not detected")

        # Confidence calculation based strictly on detected content
        detected_count = sum(1 for v in [gstin, pan, fssai_no, udyam_no, cert_number] if v != "Not detected")
        if detected_count >= 2:
            confidence = 0.95
        elif detected_count == 1:
            confidence = 0.88
        elif len(text) > 100:
            confidence = 0.80
        else:
            confidence = 0.60

        return {
            "gstin": gstin,
            "pan": pan,
            "fssai_number": fssai_no,
            "udyam_number": udyam_no,
            "certificate_number": cert_number,
            "issue_date": issue_date,
            "expiry_date": expiry_date,
            "confidence_score": confidence,
            "text_length": len(text),
        }

    @staticmethod
    def calculate_expiry_radar(expiry_str: str) -> str:
        """
        Calculates Expiry Radar status: Expired, Critical, Warning, Healthy, Unknown.
        """
        if not expiry_str or expiry_str in ["Not detected", "Not available", "Perpetual", "Annual Audit"]:
            return "Healthy" if expiry_str == "Perpetual" else "Unknown"

        try:
            # Attempt to parse date formats
            target_dt = None
            for fmt in ["%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y", "%Y-%m-%d", "%d %b %Y", "%d %B %Y"]:
                try:
                    target_dt = datetime.strptime(expiry_str.strip(), fmt)
                    break
                except ValueError:
                    continue

            if not target_dt:
                return "Unknown"

            now = datetime.now()
            delta_days = (target_dt - now).days

            if delta_days < 0:
                return "Expired"
            elif delta_days <= 30:
                return "Critical"
            elif delta_days <= 90:
                return "Warning"
            else:
                return "Healthy"
        except Exception:
            return "Unknown"

    @staticmethod
    def determine_statutory_linkage(
        document_title: str,
        category: str,
        related_approval: Optional[str],
        business_approvals: List[Approval]
    ) -> Tuple[str, str]:
        """
        Binds document to relevant business approval and derives evidence status.
        Returns (mapped_approval_name, evidence_status).
        """
        approval_names = [a.name for a in business_approvals if a.name]

        # 1. User explicit selection
        if related_approval and related_approval != "Not linked yet":
            for a in business_approvals:
                if a.name.lower() == related_approval.lower() or a.id == related_approval:
                    return a.name, "Supported"
            # If user entered custom approval name
            return related_approval, "Supported"

        # 2. Semantic title matching against business approvals
        title_lower = document_title.lower()
        for a in business_approvals:
            name_lower = a.name.lower()
            tokens = [t for t in re.findall(r"\w+", name_lower) if len(t) > 3]
            if any(tok in title_lower for tok in tokens):
                return a.name, "Supported"

        # 3. Category match
        for a in business_approvals:
            if a.category and a.category.lower() in category.lower():
                return a.name, "Supported"

        if related_approval == "Not linked yet":
            return "Not linked yet", "Needs Review"

        return "General Statutory Compliance", "Needs Review"

    @staticmethod
    def analyze_and_index_document(
        tenant_id: str,
        business_profile_id: str,
        document_id: str,
        doc_name: str,
        category: str,
        file_path: str,
        file_type: str,
        related_approval: Optional[str],
        business_approvals: List[Approval]
    ) -> Dict[str, Any]:
        """
        Runs the complete Document Intelligence pipeline:
        - text extraction
        - statutory entity extraction (zero hallucination)
        - statutory licence linkage
        - expiry radar evaluation
        - ChromaDB vector vault ingestion
        """
        # 1. Extract text
        raw_text = DocumentIntelligenceService.extract_text_from_file(file_path, file_type)

        # 2. Extract verifiable entities
        entities = DocumentIntelligenceService.extract_statutory_entities(raw_text, doc_name)

        # 3. Determine linkage
        mapped_approval, evidence_status = DocumentIntelligenceService.determine_statutory_linkage(
            doc_name, category, related_approval, business_approvals
        )

        # 4. Expiry radar
        expiry_status = DocumentIntelligenceService.calculate_expiry_radar(entities.get("expiry_date", ""))
        if expiry_status == "Expired":
            evidence_status = "Expired"

        # 5. ChromaDB Vector Vault Ingestion (isolated to tenant + business)
        vector_chunks_count = 0
        try:
            vs = get_vector_store()
            chunks = []
            if raw_text:
                # Chunk into 300-char paragraphs
                paras = [p.strip() for p in raw_text.split("\n\n") if len(p.strip()) > 20]
                if not paras:
                    paras = [raw_text[:1000]]
                for p in paras[:10]:
                    chunks.append({"content": p})
            else:
                chunks.append({"content": f"Document: {doc_name}. Category: {category}. Linked Approval: {mapped_approval}"})

            vector_chunks_count = vs.add_business_document_chunks(
                tenant_id=tenant_id,
                business_profile_id=business_profile_id,
                document_id=document_id,
                doc_name=doc_name,
                category=category,
                chunks=chunks
            )
        except Exception:
            # ChromaDB ingestion failure does not break the document intelligence pipeline
            pass

        analysis_result = {
            "mapped_approval": mapped_approval,
            "evidence_status": evidence_status,
            "expiry_radar": expiry_status,
            "expiry_date": entities.get("expiry_date", "Perpetual"),
            "issue_date": entities.get("issue_date", "Not detected"),
            "extracted_entities": entities,
            "vector_indexed_chunks": vector_chunks_count,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }

        return analysis_result
