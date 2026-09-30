import uuid
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.supplier import Supplier, SupplierDocument, SupplyItem, SupplyChainRisk
from app.models.business import BusinessProfile
from app.services.supply_chain.risk_service import SupplyChainRiskService


DEMO_DATA_BY_CATEGORY = {
    "clothing_textile": {
        "suppliers": [
            {
                "name": "Coimbatore Spinning & Yarn Mills",
                "supplier_type": "Raw Material",
                "location": "Coimbatore, Tamil Nadu",
                "country": "India",
                "products_or_materials": ["40s Combed Cotton Yarn", "Organic Knitted Greige"],
                "dependency_percentage": 82.0,
                "lead_time_days": 12,
                "status": "Active",
                "risk_status": "High",
                "contact_information": {"contact_person": "R. Sundaram", "phone": "+91 94432 10982", "email": "supply@coimbatoreyarns.in"},
                "documents": [
                    {"document_name": "GST Clear Tax Certificate FY25", "document_type": "GST Clearance", "verification_status": "Verified", "expiry_date": "31 Mar 2026"},
                    {"document_name": "OEKO-TEX Standard 100 Eco-Passport", "document_type": "Quality Certificate", "verification_status": "Expired", "expiry_date": "10 Jan 2026"}
                ]
            },
            {
                "name": "Bhavani Bio-Dyes & Chemical Works",
                "supplier_type": "Raw Material",
                "location": "Erode, Tamil Nadu",
                "country": "India",
                "products_or_materials": ["Azo-Free Reactive Dyes", "Textile Softeners"],
                "dependency_percentage": 55.0,
                "lead_time_days": 8,
                "status": "Active",
                "risk_status": "Medium",
                "contact_information": {"contact_person": "P. Murugesan", "phone": "+91 98421 55670", "email": "orders@bhavanidyes.com"},
                "documents": [
                    {"document_name": "Pollution Control PCB Consent to Operate", "document_type": "Statutory Clearance", "verification_status": "Verified", "expiry_date": "30 Jun 2027"},
                    {"document_name": "ISO 9001:2015 Quality Management", "document_type": "ISO 9001", "verification_status": "Verified", "expiry_date": "15 Dec 2026"}
                ]
            },
            {
                "name": "Surat Specialty Synthetic Blends",
                "supplier_type": "Raw Material",
                "location": "Surat, Gujarat",
                "country": "India",
                "products_or_materials": ["Recycled Polyester Microfilament", "Spandex Core Yarn"],
                "dependency_percentage": 75.0,
                "lead_time_days": 26,  # > 21 days lead time bottleneck!
                "status": "Active",
                "risk_status": "High",
                "contact_information": {"contact_person": "Anil Mehta", "phone": "+91 98251 77234", "email": "sales@suratblend.com"},
                "documents": [
                    {"document_name": "GST Tax Invoicing Ledger", "document_type": "GST Clearance", "verification_status": "Verified", "expiry_date": "31 Dec 2026"},
                    {"document_name": "Vendor Quality Compliance SLA", "document_type": "Vendor Contract", "verification_status": "Missing", "expiry_date": None}
                ]
            }
        ],
        "items": [
            {
                "name": "40s Combed Organic Cotton Yarn",
                "category": "Raw Material",
                "criticality": "Critical",
                "supplier_index": 0,
                "alternate_supplier_count": 0,  # Single source vulnerability!
                "dependency_percentage": 82.0,
                "monthly_consumption": "12,500 kg",
                "buffer_stock_days": 6  # Low buffer stock!
            },
            {
                "name": "Eco-Friendly Azo-Free Dye Pigments",
                "category": "Raw Material",
                "criticality": "High",
                "supplier_index": 1,
                "alternate_supplier_count": 2,
                "dependency_percentage": 55.0,
                "monthly_consumption": "1,800 kg",
                "buffer_stock_days": 18
            },
            {
                "name": "Spandex Elastic Core Filament",
                "category": "Raw Material",
                "criticality": "High",
                "supplier_index": 2,
                "alternate_supplier_count": 0,
                "dependency_percentage": 75.0,
                "monthly_consumption": "950 kg",
                "buffer_stock_days": 10
            }
        ]
    },
    "restaurant": {
        "suppliers": [
            {
                "name": "Nilgiris Fresh Dairy Co-op",
                "supplier_type": "Raw Material",
                "location": "Ooty, Tamil Nadu",
                "country": "India",
                "products_or_materials": ["A2 Milk", "Fresh Cream", "Unsalted Butter"],
                "dependency_percentage": 90.0,
                "lead_time_days": 2,
                "status": "Active",
                "risk_status": "High",
                "contact_information": {"contact_person": "K. Balan", "phone": "+91 94420 88711", "email": "dairy@nilgiriscoop.org"},
                "documents": [
                    {"document_name": "FSSAI Central Food Safety Registration", "document_type": "FSSAI Licence", "verification_status": "Verified", "expiry_date": "20 Nov 2026"},
                    {"document_name": "Cold Chain Thermometer Calibration Log", "document_type": "Safety Audit", "verification_status": "Expired", "expiry_date": "05 Jan 2026"}
                ]
            },
            {
                "name": "Cauvery Agri-Spice & Rice Producers",
                "supplier_type": "Raw Material",
                "location": "Thanjavur, Tamil Nadu",
                "country": "India",
                "products_or_materials": ["Seeraga Samba Rice", "Salem Guntur Chillies"],
                "dependency_percentage": 60.0,
                "lead_time_days": 6,
                "status": "Active",
                "risk_status": "Low",
                "contact_information": {"contact_person": "V. Raman", "phone": "+91 98432 44321", "email": "sales@cauveryrice.in"},
                "documents": [
                    {"document_name": "FSSAI Food Trade Licence", "document_type": "FSSAI Licence", "verification_status": "Verified", "expiry_date": "14 Aug 2027"}
                ]
            }
        ],
        "items": [
            {
                "name": "Fresh Organic A2 Cow Milk & Paneer",
                "category": "Raw Material",
                "criticality": "Critical",
                "supplier_index": 0,
                "alternate_supplier_count": 0,
                "dependency_percentage": 90.0,
                "monthly_consumption": "3,000 Litres",
                "buffer_stock_days": 2
            },
            {
                "name": "Premium Seeraga Samba Rice",
                "category": "Raw Material",
                "criticality": "High",
                "supplier_index": 1,
                "alternate_supplier_count": 1,
                "dependency_percentage": 60.0,
                "monthly_consumption": "800 kg",
                "buffer_stock_days": 20
            }
        ]
    }
}


def seed_demo_supply_chain(db: Session, business_id: str) -> Dict[str, Any]:
    """
    Safely seeds category-specific demo supply chain entities for the given business.
    Marks all seeded entities with is_demo=True.
    """
    profile = db.query(BusinessProfile).filter(BusinessProfile.id == business_id).first()
    category = (profile.business_category or "clothing_textile").lower() if profile else "clothing_textile"

    data_template = DEMO_DATA_BY_CATEGORY.get(category, DEMO_DATA_BY_CATEGORY["clothing_textile"])

    # Clean up prior demo entities first
    cleanup_demo_supply_chain(db, business_id)

    created_suppliers = []
    for s_data in data_template["suppliers"]:
        sup = Supplier(
            id=str(uuid.uuid4()),
            business_id=business_id,
            name=f"[DEMO DATA] {s_data['name']}",
            supplier_type=s_data["supplier_type"],
            location=s_data["location"],
            country=s_data["country"],
            products_or_materials=s_data["products_or_materials"],
            dependency_percentage=s_data["dependency_percentage"],
            lead_time_days=s_data["lead_time_days"],
            status=s_data["status"],
            contact_information=s_data.get("contact_information"),
            risk_status=s_data["risk_status"],
            is_demo=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(sup)
        db.flush()

        for doc in s_data.get("documents", []):
            s_doc = SupplierDocument(
                id=str(uuid.uuid4()),
                supplier_id=sup.id,
                document_name=f"[DEMO DATA] {doc['document_name']}",
                document_type=doc["document_type"],
                verification_status=doc["verification_status"],
                expiry_date=doc.get("expiry_date"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(s_doc)

        created_suppliers.append(sup)

    created_items = []
    for item_data in data_template["items"]:
        sup_idx = item_data.get("supplier_index", 0)
        primary_sup_id = created_suppliers[sup_idx].id if sup_idx < len(created_suppliers) else None

        item = SupplyItem(
            id=str(uuid.uuid4()),
            business_id=business_id,
            name=f"[DEMO DATA] {item_data['name']}",
            category=item_data["category"],
            criticality=item_data["criticality"],
            primary_supplier_id=primary_sup_id,
            alternate_supplier_count=item_data["alternate_supplier_count"],
            dependency_percentage=item_data["dependency_percentage"],
            monthly_consumption=item_data.get("monthly_consumption"),
            buffer_stock_days=item_data["buffer_stock_days"],
            is_demo=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(item)
        created_items.append(item)

    db.commit()

    # Automatically run deterministic risk detection on seeded data
    detected_risks = SupplyChainRiskService.detect_and_sync_risks(db, business_id)

    return {
        "status": "SEEDED",
        "business_id": business_id,
        "suppliers_seeded": len(created_suppliers),
        "items_seeded": len(created_items),
        "risks_detected": len(detected_risks)
    }


def cleanup_demo_supply_chain(db: Session, business_id: str) -> int:
    """
    Safely removes all is_demo=True supply chain records for the given business.
    """
    risks_del = db.query(SupplyChainRisk).filter(
        SupplyChainRisk.business_id == business_id,
        SupplyChainRisk.is_demo == True
    ).delete(synchronize_session=False)

    items_del = db.query(SupplyItem).filter(
        SupplyItem.business_id == business_id,
        SupplyItem.is_demo == True
    ).delete(synchronize_session=False)

    suppliers = db.query(Supplier).filter(
        Supplier.business_id == business_id,
        Supplier.is_demo == True
    ).all()

    sup_count = len(suppliers)
    for s in suppliers:
        db.delete(s)

    db.commit()
    return sup_count + items_del + risks_del
