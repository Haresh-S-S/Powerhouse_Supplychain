import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.supplier import Supplier, SupplierDocument, SupplyItem, SupplyChainRisk


class SupplyChainRiskService:
    @staticmethod
    def calculate_resilience_score(db: Session, business_id: str) -> Dict[str, Any]:
        """
        Calculates a deterministic 0-100 Resilience Score for a business supply chain.
        Deductions are based on verified structural vulnerabilities.
        """
        suppliers = db.query(Supplier).filter(Supplier.business_id == business_id).all()
        items = db.query(SupplyItem).filter(SupplyItem.business_id == business_id).all()
        risks = db.query(SupplyChainRisk).filter(
            SupplyChainRisk.business_id == business_id,
            SupplyChainRisk.status.notin_(["RESOLVED", "DISMISSED"])
        ).all()

        if not suppliers and not items:
            return {
                "score": 50,
                "rating": "Moderate",
                "total_suppliers": 0,
                "critical_suppliers": 0,
                "total_items": 0,
                "critical_items": 0,
                "single_source_count": 0,
                "missing_docs_count": 0,
                "lead_time_avg": 0.0,
            }

        score = 100.0

        # 1. Single Source Critical Items Penalty (up to -30 pts)
        single_source_items = [
            i for i in items
            if i.criticality in ["Critical", "High"] and (i.alternate_supplier_count == 0 or i.dependency_percentage >= 70.0)
        ]
        single_source_penalty = min(30.0, len(single_source_items) * 10.0)
        score -= single_source_penalty

        # 2. Missing / Expired Supplier Documentation Penalty (up to -25 pts)
        missing_docs_count = 0
        for s in suppliers:
            docs = s.documents or []
            if not docs:
                missing_docs_count += 1
            else:
                has_expired_or_missing = any(d.verification_status in ["Missing", "Expired"] for d in docs)
                if has_expired_or_missing:
                    missing_docs_count += 1
        docs_penalty = min(25.0, missing_docs_count * 8.0)
        score -= docs_penalty

        # 3. Extended Lead Time Penalty (up to -20 pts)
        long_lead_suppliers = [s for s in suppliers if s.lead_time_days > 21]
        lead_time_penalty = min(20.0, len(long_lead_suppliers) * 7.0)
        score -= lead_time_penalty

        # 4. Critical Buffer Stock Depletion (up to -15 pts)
        low_buffer_items = [i for i in items if i.buffer_stock_days < 7]
        buffer_penalty = min(15.0, len(low_buffer_items) * 5.0)
        score -= buffer_penalty

        final_score = max(10, min(100, int(round(score))))

        if final_score >= 85:
            rating = "Excellent"
        elif final_score >= 70:
            rating = "Resilient"
        elif final_score >= 50:
            rating = "Moderate"
        elif final_score >= 35:
            rating = "Vulnerable"
        else:
            rating = "High Risk"

        critical_suppliers = len([s for s in suppliers if s.risk_status in ["High", "Critical"]])
        critical_items = len([i for i in items if i.criticality in ["Critical", "High"]])
        lead_time_avg = (
            sum(s.lead_time_days for s in suppliers) / len(suppliers)
            if suppliers else 0.0
        )

        return {
            "score": final_score,
            "rating": rating,
            "total_suppliers": len(suppliers),
            "critical_suppliers": critical_suppliers,
            "total_items": len(items),
            "critical_items": critical_items,
            "single_source_count": len(single_source_items),
            "missing_docs_count": missing_docs_count,
            "lead_time_avg": round(lead_time_avg, 1),
        }

    @staticmethod
    def detect_and_sync_risks(db: Session, business_id: str) -> List[SupplyChainRisk]:
        """
        Runs deterministic risk detection algorithms over business supply chain entities.
        Ensures idempotency: updates existing active risks or creates new ones.
        """
        suppliers = db.query(Supplier).filter(Supplier.business_id == business_id).all()
        items = db.query(SupplyItem).filter(SupplyItem.business_id == business_id).all()

        detected_risks = []

        # 1. Single Supplier Dependency Risk
        for item in items:
            if item.criticality in ["Critical", "High"] and (item.alternate_supplier_count == 0 or item.dependency_percentage >= 70.0):
                primary_sup = item.primary_supplier
                sup_name = primary_sup.name if primary_sup else "Unassigned Primary Vendor"
                risk_title = f"Single Source Dependency: {item.name}"

                existing = db.query(SupplyChainRisk).filter(
                    SupplyChainRisk.business_id == business_id,
                    SupplyChainRisk.supply_item_id == item.id,
                    SupplyChainRisk.category == "Single Supplier Dependency",
                    SupplyChainRisk.status.notin_(["RESOLVED", "DISMISSED"])
                ).first()

                evidence = {
                    "supply_item": item.name,
                    "criticality": item.criticality,
                    "dependency_percentage": item.dependency_percentage,
                    "primary_supplier": sup_name,
                    "alternate_supplier_count": item.alternate_supplier_count,
                    "buffer_stock_days": item.buffer_stock_days,
                    "benchmark_rule": "Items marked Critical/High must have at least 1 qualified secondary source or dependency < 70%."
                }

                if not existing:
                    risk = SupplyChainRisk(
                        id=str(uuid.uuid4()),
                        business_id=business_id,
                        supplier_id=item.primary_supplier_id,
                        supply_item_id=item.id,
                        title=risk_title,
                        category="Single Supplier Dependency",
                        priority="Critical" if item.criticality == "Critical" else "High",
                        severity="Critical",
                        evidence=evidence,
                        issue=f"{item.name} has {item.dependency_percentage}% sole reliance on {sup_name} with 0 verified secondary supplier backups.",
                        cause=f"Procurement concentration on a single source without multi-vendor qualifying framework.",
                        recommended_action=f"Initiate vendor pre-qualification audit for an alternate supplier and negotiate 30% secondary allocation quota.",
                        estimated_cost=25000.0,
                        estimated_risk_reduction=65.0,
                        effort="Medium",
                        confidence=0.92,
                        status="RECOMMENDED",
                        policy_check_status="PASS",
                        is_demo=item.is_demo,
                        detected_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    db.add(risk)
                    detected_risks.append(risk)
                else:
                    existing.evidence = evidence
                    existing.updated_at = datetime.utcnow()
                    detected_risks.append(existing)

        # 2. Missing or Expired Supplier Documentation
        for sup in suppliers:
            docs = sup.documents or []
            missing_types = []
            if not docs:
                missing_types.append("Vendor Compliance Dossier & GST Clearance")
            else:
                for d in docs:
                    if d.verification_status in ["Missing", "Expired"]:
                        missing_types.append(f"{d.document_type} ({d.verification_status})")

            if missing_types:
                risk_title = f"Compliance Documentation Gap: {sup.name}"
                existing = db.query(SupplyChainRisk).filter(
                    SupplyChainRisk.business_id == business_id,
                    SupplyChainRisk.supplier_id == sup.id,
                    SupplyChainRisk.category == "Missing Documentation",
                    SupplyChainRisk.status.notin_(["RESOLVED", "DISMISSED"])
                ).first()

                evidence = {
                    "supplier_name": sup.name,
                    "supplier_type": sup.supplier_type,
                    "missing_or_expired_documents": missing_types,
                    "statutory_mandate": "Verified GST, safety clearance, and vendor contract required under statutory audit rules."
                }

                if not existing:
                    risk = SupplyChainRisk(
                        id=str(uuid.uuid4()),
                        business_id=business_id,
                        supplier_id=sup.id,
                        supply_item_id=None,
                        title=risk_title,
                        category="Missing Documentation",
                        priority="High",
                        severity="Warning",
                        evidence=evidence,
                        issue=f"{sup.name} has unverified or expired vendor compliance credentials: {', '.join(missing_types)}.",
                        cause="Periodic vendor renewal audits were not scheduled prior to document expiry date.",
                        recommended_action="Request updated GST compliance filing, quality certificate, and statutory undertaking via Document Vault.",
                        estimated_cost=0.0,
                        estimated_risk_reduction=40.0,
                        effort="Low",
                        confidence=0.95,
                        status="RECOMMENDED",
                        policy_check_status="PASS",
                        is_demo=sup.is_demo,
                        detected_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    db.add(risk)
                    detected_risks.append(risk)
                else:
                    existing.evidence = evidence
                    existing.updated_at = datetime.utcnow()
                    detected_risks.append(existing)

        # 3. Extended Lead Time Risk (> 21 days on active items)
        for sup in suppliers:
            if sup.lead_time_days > 21 and sup.status == "Active":
                risk_title = f"Extended Lead Time Vulnerability: {sup.name}"
                existing = db.query(SupplyChainRisk).filter(
                    SupplyChainRisk.business_id == business_id,
                    SupplyChainRisk.supplier_id == sup.id,
                    SupplyChainRisk.category == "Extended Lead Time",
                    SupplyChainRisk.status.notin_(["RESOLVED", "DISMISSED"])
                ).first()

                evidence = {
                    "supplier_name": sup.name,
                    "lead_time_days": sup.lead_time_days,
                    "location": f"{sup.location}, {sup.country}",
                    "industry_threshold": "Maximum 21 business days before safety stock depletion."
                }

                if not existing:
                    risk = SupplyChainRisk(
                        id=str(uuid.uuid4()),
                        business_id=business_id,
                        supplier_id=sup.id,
                        supply_item_id=None,
                        title=risk_title,
                        category="Extended Lead Time",
                        priority="Medium",
                        severity="Warning",
                        evidence=evidence,
                        issue=f"{sup.name} operates with a {sup.lead_time_days}-day fulfilment lead time, creating replenishment lag risks.",
                        cause=f"Transit distances and non-buffered production cycle from {sup.location}.",
                        recommended_action=f"Establish local consignment stock buffer or enter into a Service Level Agreement (SLA) with guaranteed 14-day delivery.",
                        estimated_cost=15000.0,
                        estimated_risk_reduction=50.0,
                        effort="Medium",
                        confidence=0.88,
                        status="RECOMMENDED",
                        policy_check_status="PASS",
                        is_demo=sup.is_demo,
                        detected_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    db.add(risk)
                    detected_risks.append(risk)
                else:
                    existing.evidence = evidence
                    existing.updated_at = datetime.utcnow()
                    detected_risks.append(existing)

        db.commit()
        return detected_risks
