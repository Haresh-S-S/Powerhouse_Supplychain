import re
import hashlib
from typing import List, Dict, Any


def generate_content_hash(text: str) -> str:
    """Computes SHA-256 content hash of normalized text."""
    normalized = " ".join(text.strip().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class StatutoryChunkItem(dict):
    """Dictionary subclass that allows attribute-style access for test and contract compatibility."""
    def __getattr__(self, name):
        if name in self:
            return self[name]
        if name == "source_document_id":
            return self.get("source_id", "")
        if name == "statutory_authority":
            return self.get("authority", "")
        raise AttributeError(f"'StatutoryChunkItem' object has no attribute '{name}'")


class StatutoryChunker:
    """
    Statutory-aware chunker that respects Indian legal structure:
    Acts, Chapters, Sections, Subsections, Rules, and Circulars.
    Preserves legal provenance and attaches metadata to every chunk.
    """

    @classmethod
    def chunk_text(
        cls,
        text: str,
        source_id: str,
        category: str = "general_statutory",
        jurisdiction: str = "Central",
        source_title: str = "",
        authority: str = "",
        document_id: str = "",
        verification_status: str = "VERIFIED",
        default_section: str = ""
    ) -> List[StatutoryChunkItem]:
        raw_chunks = cls.chunk_statutory_text(
            text=text,
            source_id=source_id,
            category=category,
            jurisdiction=jurisdiction,
            document_id=document_id,
            verification_status=verification_status,
            default_section=default_section
        )
        items = []
        for c in raw_chunks:
            item = StatutoryChunkItem(c)
            item["source_title"] = source_title
            item["authority"] = authority
            items.append(item)
        return items

    @staticmethod
    def chunk_statutory_text(
        text: str,
        source_id: str,
        category: str = "general_statutory",
        jurisdiction: str = "Central",
        document_id: str = "",
        verification_status: str = "VERIFIED",
        default_section: str = ""
    ) -> List[Dict[str, Any]]:
        if not text or not text.strip():
            return []

        lines = text.strip().split("\n")
        chunks = []
        current_chapter = ""
        current_section = default_section or "General"
        current_rule = ""
        current_buffer = []

        def flush_chunk():
            nonlocal current_buffer
            raw_content = "\n".join(current_buffer).strip()
            if len(raw_content) >= 40:  # Ignore trivial headers
                chunk_index = len(chunks) + 1
                sec_clean = re.sub(r"[^\w\d]", "-", current_section.lower())[:30].strip("-")
                chunk_id = f"{source_id}-{sec_clean}-chk{chunk_index}"
                full_content = raw_content
                if current_chapter and current_chapter not in full_content:
                    full_content = f"{current_chapter} - {current_section}\n{full_content}"
                c_hash = generate_content_hash(full_content)
                chunks.append({
                    "chunk_id": chunk_id,
                    "source_id": source_id,
                    "document_id": document_id,
                    "chapter": current_chapter or "Statutory Provisions",
                    "section": current_section,
                    "rule": current_rule,
                    "content": full_content,
                    "content_hash": c_hash,
                    "jurisdiction": jurisdiction,
                    "category": category,
                    "verification_status": verification_status
                })
            current_buffer = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Check for Chapter marker
            if re.match(r"^(?:CHAPTER\s+[IVXLCDM\d]+|PART\s+[IVXLCDM\d]+)", stripped, re.IGNORECASE):
                if current_buffer:
                    flush_chunk()
                current_chapter = stripped
                continue

            # Check for Section marker (e.g., Section 31, Sec 25)
            sec_match = re.match(r"^(?:Section|Sec\.)\s+(\d+[A-Za-z]*)", stripped, re.IGNORECASE)
            if sec_match:
                if current_buffer:
                    flush_chunk()
                current_section = f"Section {sec_match.group(1)}"
                current_buffer.append(stripped)
                continue

            # Check for Rule or Circular marker
            rule_match = re.match(r"^(?:Rule|Circular|Order|Regulation)\s+([^\n:]+)", stripped, re.IGNORECASE)
            if rule_match:
                if len("\n".join(current_buffer)) >= 120:
                    flush_chunk()
                current_rule = stripped[:60]
                current_buffer.append(stripped)
                continue

            current_buffer.append(stripped)

            # Break on semantic statutory boundaries if exceeding ~900 chars
            if len("\n".join(current_buffer)) > 900 and stripped.endswith((".", ";", ":")):
                flush_chunk()

        if current_buffer:
            flush_chunk()

        if not chunks and len(text.strip()) > 0:
            c_hash = generate_content_hash(text)
            chunks.append({
                "chunk_id": f"{source_id}-gen-chk1",
                "source_id": source_id,
                "document_id": document_id,
                "chapter": "Statutory General",
                "section": default_section or "Statutory Provisions",
                "rule": "",
                "content": text.strip(),
                "content_hash": c_hash,
                "jurisdiction": jurisdiction,
                "category": category,
                "verification_status": verification_status
            })

        return chunks
