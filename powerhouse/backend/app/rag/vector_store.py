import os
import re
import math
import hashlib
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings


class StatutoryDenseEmbeddingFunction(EmbeddingFunction[Documents]):
    """
    Self-contained, deterministic 384-dimensional dense semantic embedding function.
    Runs 100% locally and offline without external API keys or network latency.
    Produces unit-normalized dense vectors suitable for cosine / L2 similarity.
    """
    STOPWORDS = {'what', 'are', 'the', 'is', 'a', 'an', 'and', 'or', 'for', 'my', 'in', 'of', 'to', 'do', 'i', 'needed', 'applies', 'apply', 'with', 'from'}

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            embeddings.append(self._embed_single(text))
        return embeddings

    def name(self) -> str:
        return "statutory_dense_embedding"

    def get_config(self) -> Dict[str, Any]:
        return {"dimension": self.dimension}

    @classmethod
    def build_from_config(cls, config: Dict[str, Any]) -> "StatutoryDenseEmbeddingFunction":
        return cls(dimension=config.get("dimension", 384))

    def _embed_single(self, text: str) -> List[float]:
        vec = [0.0] * self.dimension
        if not text:
            vec[0] = 1.0
            return vec

        raw_tokens = [t.lower() for t in re.findall(r"\w+", text) if len(t) > 1]
        if not raw_tokens:
            vec[0] = 1.0
            return vec

        for i, token in enumerate(raw_tokens):
            weight = 0.2 if token in self.STOPWORDS else 1.0
            # 1-gram dense projection
            h1 = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx1 = h1 % self.dimension
            sign1 = 1.0 if (h1 >> 8) % 2 == 0 else -1.0
            vec[idx1] += sign1 * weight * 1.5

            # 2-gram dense projection
            if i < len(raw_tokens) - 1:
                bigram = f"{token}_{raw_tokens[i+1]}"
                h2 = int(hashlib.sha1(bigram.encode("utf-8")).hexdigest(), 16)
                idx2 = h2 % self.dimension
                sign2 = 1.0 if (h2 >> 8) % 2 == 0 else -1.0
                vec[idx2] += sign2 * weight * 2.0

        # L2 unit normalization
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 1e-9:
            vec = [x / norm for x in vec]
        else:
            vec[0] = 1.0
        return vec


class VectorStoreService:
    """
    Manages local ChromaDB collections with strict tenant isolation and regulatory separation.
    """
    _instance = None

    def __init__(self, persist_dir: Optional[str] = None):
        if not persist_dir:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            persist_dir = os.path.join(base_dir, "data", "chroma_db")
        os.makedirs(persist_dir, exist_ok=True)
        self.persist_dir = persist_dir

        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.embedding_fn = StatutoryDenseEmbeddingFunction()

        # 1. Global Regulatory Knowledge Collection
        self.regulatory_collection = self.client.get_or_create_collection(
            name="regulatory_knowledge",
            embedding_function=self.embedding_fn,
            metadata={"description": "Authoritative Indian statutory compliance rules and gazettes"}
        )

        # 2. Tenant-Isolated Business Document Collection
        self.business_doc_collection = self.client.get_or_create_collection(
            name="business_documents",
            embedding_function=self.embedding_fn,
            metadata={"description": "Tenant-scoped business files and document intelligence extracts"}
        )

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ----------------------------------------------------------------------
    # Regulatory Knowledge Operations (Global, Filtered by Verification)
    # ----------------------------------------------------------------------

    def add_regulatory_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        if not chunks:
            return 0

        ids = []
        documents = []
        metadatas = []

        for chk in chunks:
            cid = chk["chunk_id"]
            ids.append(cid)
            documents.append(chk["content"])
            metadatas.append({
                "source_id": chk.get("source_id", ""),
                "act_name": chk.get("act_name", ""),
                "authority": chk.get("authority", ""),
                "title": chk.get("title", ""),
                "section": chk.get("section", "General"),
                "chapter": chk.get("chapter", ""),
                "category": chk.get("category", "general_statutory"),
                "jurisdiction": chk.get("jurisdiction", "Central"),
                "verification_status": chk.get("verification_status", "VERIFIED"),
                "content_hash": chk.get("content_hash", "")
            })

        self.regulatory_collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        return len(ids)

    def query_regulatory(
        self,
        query_text: str,
        category: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        top_k: int = 5,
        only_verified: bool = True
    ) -> List[Dict[str, Any]]:
        where_clauses = []
        if only_verified:
            where_clauses.append({"verification_status": {"$in": ["VERIFIED", "ACTIVE"]}})

        # Category filter: Allow matching category or universal 'general_statutory'
        if category and category != "all":
            where_clauses.append({"category": {"$in": [category, "general_statutory"]}})

        where_filter = None
        if len(where_clauses) == 1:
            where_filter = where_clauses[0]
        elif len(where_clauses) > 1:
            where_filter = {"$and": where_clauses}

        results = self.regulatory_collection.query(
            query_texts=[query_text],
            n_results=top_k,
            where=where_filter
        )

        formatted = []
        if results and results["ids"] and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                cid = results["ids"][0][i]
                doc = results["documents"][0][i]
                meta = results["metadatas"][0][i]
                dist = results["distances"][0][i] if "distances" in results and results["distances"] else 0.0
                cos_sim = max(0.0, 1.0 - (dist / 2.0)) if dist is not None else 0.0
                if cos_sim <= 0.03:
                    calibrated_sem = 0.0
                else:
                    calibrated_sem = min(1.0, 0.40 + (cos_sim - 0.03) * 3.0)
                formatted.append({
                    "chunk_id": cid,
                    "content": doc,
                    "metadata": meta,
                    "distance": dist,
                    "semantic_score": round(calibrated_sem, 4)
                })
        return formatted

    # ----------------------------------------------------------------------
    # Business Document Operations (STRICTLY Tenant & Business Scoped)
    # ----------------------------------------------------------------------

    def add_business_document_chunks(
        self,
        tenant_id: str,
        business_profile_id: str,
        document_id: str,
        doc_name: str,
        category: str,
        chunks: List[Dict[str, Any]]
    ) -> int:
        if not chunks or not tenant_id or not business_profile_id:
            return 0

        ids = []
        documents = []
        metadatas = []

        for i, chk in enumerate(chunks):
            cid = f"bdoc-{document_id}-{i+1}"
            ids.append(cid)
            content = chk.get("content", "")
            documents.append(content)
            metadatas.append({
                "tenant_id": str(tenant_id),
                "business_profile_id": str(business_profile_id),
                "document_id": str(document_id),
                "doc_name": str(doc_name),
                "category": str(category),
                "source_type": "BUSINESS_DOCUMENT"
            })

        self.business_doc_collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        return len(ids)

    def query_business_documents(
        self,
        tenant_id: str,
        business_profile_id: str,
        query_text: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        where_filter = {
            "$and": [
                {"tenant_id": str(tenant_id)},
                {"business_profile_id": str(business_profile_id)}
            ]
        }

        results = self.business_doc_collection.query(
            query_texts=[query_text],
            n_results=top_k,
            where=where_filter
        )

        formatted = []
        if results and results["ids"] and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                cid = results["ids"][0][i]
                doc = results["documents"][0][i]
                meta = results["metadatas"][0][i]
                dist = results["distances"][0][i] if "distances" in results and results["distances"] else 0.0
                sim = max(0.0, min(1.0, 1.0 - (dist / 2.0))) if dist is not None else 0.85
                formatted.append({
                    "chunk_id": cid,
                    "content": doc,
                    "metadata": meta,
                    "source_type": "BUSINESS_DOCUMENT",
                    "semantic_score": round(sim, 4)
                })
        return formatted

    def delete_business_document(self, tenant_id: str, business_profile_id: str, document_id: str):
        where_filter = {
            "$and": [
                {"tenant_id": str(tenant_id)},
                {"business_profile_id": str(business_profile_id)},
                {"document_id": str(document_id)}
            ]
        }
        self.business_doc_collection.delete(where=where_filter)

    def get_regulatory_collection(self):
        return self.regulatory_collection

    def get_business_doc_collection(self):
        return self.business_doc_collection


def get_vector_store() -> VectorStoreService:
    return VectorStoreService.get_instance()
