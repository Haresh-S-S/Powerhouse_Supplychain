import uuid
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.workforce import EmployeeProfile, RoleProfile, SkillGap, LearningPath
from app.models.business import BusinessProfile
from app.services.workforce.intelligence_service import WorkforceIntelligenceService


DEMO_WORKFORCE_BY_CATEGORY = {
    "clothing_textile": {
        "roles": [
            {
                "role_name": "Knitting & Weaving Supervisor",
                "department": "Production Operations",
                "required_skills": [
                    {"skill": "Loom Operations", "level": "Advanced", "category": "Mechanical"},
                    {"skill": "Digital IoT Loom Telemetry", "level": "Intermediate", "category": "Industry 4.0"},
                    {"skill": "Yarn Tension Quality Control", "level": "Advanced", "category": "Quality Assurance"}
                ],
                "optional_skills": ["ERP Shift Logging", "Energy Monitoring"]
            },
            {
                "role_name": "Textile Quality Inspector",
                "department": "Quality Assurance",
                "required_skills": [
                    {"skill": "Fabric Defect Classification", "level": "Advanced", "category": "Quality Assurance"},
                    {"skill": "OEKO-TEX Standard 100 Chemical Compliance", "level": "Intermediate", "category": "Statutory Safety"},
                    {"skill": "Colorfastness Spectrophotometry", "level": "Intermediate", "category": "Laboratory Testing"}
                ],
                "optional_skills": ["Digital Audit Checklists"]
            },
            {
                "role_name": "ETP Wastewater Plant Technician",
                "department": "Environmental & Safety",
                "required_skills": [
                    {"skill": "Effluent Neutralization & Coagulation", "level": "Advanced", "category": "Environmental"},
                    {"skill": "Online Continuous Effluent Monitoring (OCEMS)", "level": "Intermediate", "category": "Pollution Control"},
                    {"skill": "Hazardous Sludge Manifest Documentation", "level": "Intermediate", "category": "Compliance"}
                ],
                "optional_skills": ["Zero Liquid Discharge (ZLD) Systems"]
            }
        ],
        "employees": [
            {
                "employee_reference": "EMP-TX-101",
                "role": "Knitting & Weaving Supervisor",
                "department": "Production Operations",
                "experience_years": 4.5,
                "current_skills": ["Loom Operations", "Yarn Tension Quality Control", "Shift Scheduling"],
                "preferred_learning_areas": ["Industry 4.0 Digital Controls", "Automated Defect Detection"],
                "accessibility_preferences": ["Screen Reader Compatible", "Flexible Self-Paced Modules"]
            },
            {
                "employee_reference": "EMP-TX-102",
                "role": "Textile Quality Inspector",
                "department": "Quality Assurance",
                "experience_years": 2.0,
                "current_skills": ["Fabric Defect Classification", "Visual Inspection"],
                "preferred_learning_areas": ["Chemical Safety Certifications", "Eco-Passport Audits"],
                "accessibility_preferences": ["Captioned Video", "High-Contrast Diagrams"]
            },
            {
                "employee_reference": "EMP-TX-103",
                "role": "ETP Wastewater Plant Technician",
                "department": "Environmental & Safety",
                "experience_years": 3.2,
                "current_skills": ["Effluent Neutralization & Coagulation", "Basic Chemistry Testing"],
                "preferred_learning_areas": ["Pollution Control Board Telemetry", "Automated Sensor Calibration"],
                "accessibility_preferences": ["Audio-Guided Instructions"]
            }
        ]
    },
    "restaurant": {
        "roles": [
            {
                "role_name": "Food Safety & Hygiene Supervisor",
                "department": "Kitchen Operations",
                "required_skills": [
                    {"skill": "FSSAI FoSCoS Regulatory Norms", "level": "Advanced", "category": "Compliance"},
                    {"skill": "HACCP Food Safety Management Plan", "level": "Advanced", "category": "Food Safety"},
                    {"skill": "Cold Chain Thermometer Calibration", "level": "Intermediate", "category": "Safety Auditing"}
                ],
                "optional_skills": ["Allergen Matrix Mapping"]
            },
            {
                "role_name": "Commercial Kitchen Lead Cook",
                "department": "Culinary",
                "required_skills": [
                    {"skill": "Food Preparation & Standard Recipes", "level": "Advanced", "category": "Culinary"},
                    {"skill": "Cross-Contamination & Allergen Prevention", "level": "Intermediate", "category": "Food Safety"},
                    {"skill": "Kitchen Hood Fire Suppression Protocol", "level": "Intermediate", "category": "Safety"}
                ],
                "optional_skills": ["Nutritional Portioning"]
            }
        ],
        "employees": [
            {
                "employee_reference": "EMP-FD-201",
                "role": "Food Safety & Hygiene Supervisor",
                "department": "Kitchen Operations",
                "experience_years": 3.0,
                "current_skills": ["FSSAI FoSCoS Regulatory Norms", "General Sanitation"],
                "preferred_learning_areas": ["HACCP Implementation", "NABL Lab Water Testing"],
                "accessibility_preferences": ["Captioned Video"]
            },
            {
                "employee_reference": "EMP-FD-202",
                "role": "Commercial Kitchen Lead Cook",
                "department": "Culinary",
                "experience_years": 2.5,
                "current_skills": ["Food Preparation & Standard Recipes", "Knife Skills"],
                "preferred_learning_areas": ["Fire Suppression Readiness", "Allergen Management"],
                "accessibility_preferences": ["Hands-On Visual Guides"]
            }
        ]
    },
    "retail": {
        "roles": [
            {
                "role_name": "Store Operations & Compliance Manager",
                "department": "Store Management",
                "required_skills": [
                    {"skill": "Shops & Establishments Compliance", "level": "Advanced", "category": "Statutory"},
                    {"skill": "Inventory Loss Prevention", "level": "Advanced", "category": "Operations"},
                    {"skill": "Legal Metrology Verification", "level": "Intermediate", "category": "Compliance"}
                ],
                "optional_skills": ["POS Reconciliation", "Customer Grievance Redressal"]
            },
            {
                "role_name": "Inventory & Warehouse Controller",
                "department": "Logistics & Inventory",
                "required_skills": [
                    {"skill": "Barcode/RFID Scanning & Tagging", "level": "Intermediate", "category": "Logistics"},
                    {"skill": "FIFO Stock Rotation & Expiry Audits", "level": "Advanced", "category": "Inventory"},
                    {"skill": "Warehouse Material Handling Safety", "level": "Intermediate", "category": "Safety"}
                ],
                "optional_skills": ["Cycle Counting", "Vendor Return Processing"]
            }
        ],
        "employees": [
            {
                "employee_reference": "EMP-RT-301",
                "role": "Store Operations & Compliance Manager",
                "department": "Store Management",
                "experience_years": 4.0,
                "current_skills": ["Inventory Loss Prevention", "POS Reconciliation"],
                "preferred_learning_areas": ["Shops & Establishments Compliance", "Legal Metrology Verification"],
                "accessibility_preferences": ["Large Print UI", "Self-Paced Modules"]
            },
            {
                "employee_reference": "EMP-RT-302",
                "role": "Inventory & Warehouse Controller",
                "department": "Logistics & Inventory",
                "experience_years": 2.2,
                "current_skills": ["Barcode/RFID Scanning & Tagging", "Cycle Counting"],
                "preferred_learning_areas": ["FIFO Stock Rotation & Expiry Audits", "Warehouse Material Handling Safety"],
                "accessibility_preferences": ["Vernacular Audio (Tamil)"]
            }
        ]
    },
    "manufacturing": {
        "roles": [
            {
                "role_name": "Plant Safety & Operations Supervisor",
                "department": "Plant Operations",
                "required_skills": [
                    {"skill": "Factories Act 1948 Safety Compliance", "level": "Advanced", "category": "Statutory"},
                    {"skill": "Assembly Line Machine Guarding", "level": "Advanced", "category": "Safety"},
                    {"skill": "Hazardous Waste Manifest & MSDS", "level": "Intermediate", "category": "Safety"}
                ],
                "optional_skills": ["Overall Equipment Effectiveness (OEE)", "5S Workplace Audit"]
            },
            {
                "role_name": "Industrial Quality Inspector",
                "department": "Quality Assurance",
                "required_skills": [
                    {"skill": "Precision Caliper & Micrometer Metrology", "level": "Advanced", "category": "Quality Assurance"},
                    {"skill": "Statistical Process Control (SPC)", "level": "Intermediate", "category": "Analytics"},
                    {"skill": "Non-Conformance Report (NCR) Logging", "level": "Intermediate", "category": "Quality"}
                ],
                "optional_skills": ["ISO 9001 Root Cause Analysis"]
            }
        ],
        "employees": [
            {
                "employee_reference": "EMP-MF-401",
                "role": "Plant Safety & Operations Supervisor",
                "department": "Plant Operations",
                "experience_years": 5.0,
                "current_skills": ["Assembly Line Machine Guarding", "5S Workplace Audit"],
                "preferred_learning_areas": ["Factories Act 1948 Safety Compliance", "Hazardous Waste Manifest & MSDS"],
                "accessibility_preferences": ["Screen Reader Compatible", "Audio Walkthroughs"]
            },
            {
                "employee_reference": "EMP-MF-402",
                "role": "Industrial Quality Inspector",
                "department": "Quality Assurance",
                "experience_years": 3.1,
                "current_skills": ["Precision Caliper & Micrometer Metrology"],
                "preferred_learning_areas": ["Statistical Process Control (SPC)", "Non-Conformance Report (NCR) Logging"],
                "accessibility_preferences": ["High-Contrast UI", "Visual Step-by-Step"]
            }
        ]
    },
    "jewellery": {
        "roles": [
            {
                "role_name": "BIS Hallmarking & HUID In-Charge",
                "department": "Regulatory Quality",
                "required_skills": [
                    {"skill": "BIS 6-Digit HUID Verification", "level": "Advanced", "category": "Compliance"},
                    {"skill": "XRF Precious Metal Assay Testing", "level": "Advanced", "category": "Laboratory"},
                    {"skill": "PMLA FIU-IND High Value Cash Reporting", "level": "Intermediate", "category": "Statutory"}
                ],
                "optional_skills": ["Precious Stone Weighing Norms", "Tamper-Evident Bagging"]
            },
            {
                "role_name": "Showroom Custody & Security Controller",
                "department": "Security & Custody",
                "required_skills": [
                    {"skill": "Vault Dual-Custody Key Protocol", "level": "Advanced", "category": "Security"},
                    {"skill": "Daily Physical Gold Stock Reconciliation", "level": "Advanced", "category": "Custody"},
                    {"skill": "Fire & Intrusion Alarm SOPs", "level": "Intermediate", "category": "Safety"}
                ],
                "optional_skills": ["CCTV Evidence Preservation"]
            }
        ],
        "employees": [
            {
                "employee_reference": "EMP-JW-501",
                "role": "BIS Hallmarking & HUID In-Charge",
                "department": "Regulatory Quality",
                "experience_years": 3.5,
                "current_skills": ["XRF Precious Metal Assay Testing", "Precious Stone Weighing Norms"],
                "preferred_learning_areas": ["BIS 6-Digit HUID Verification", "PMLA FIU-IND High Value Cash Reporting"],
                "accessibility_preferences": ["Captioned Video", "Digital Checklist"]
            }
        ]
    }
}


def seed_demo_workforce(db: Session, business_id: str) -> Dict[str, Any]:
    """
    Safely seeds category-specific demo workforce profiles for the given business.
    Marks all seeded entities with is_demo=True.
    """
    profile = db.query(BusinessProfile).filter(BusinessProfile.id == business_id).first()
    raw_cat = (profile.business_category or profile.industry or "clothing_textile").lower() if profile else "clothing_textile"
    if "restaurant" in raw_cat or "food" in raw_cat or "dining" in raw_cat:
        category = "restaurant"
    elif "retail" in raw_cat or "store" in raw_cat or "shop" in raw_cat:
        category = "retail"
    elif "manufactur" in raw_cat or "factory" in raw_cat or "industrial" in raw_cat:
        category = "manufacturing"
    elif "jewel" in raw_cat or "gold" in raw_cat:
        category = "jewellery"
    else:
        category = "clothing_textile"

    data_template = DEMO_WORKFORCE_BY_CATEGORY.get(category, DEMO_WORKFORCE_BY_CATEGORY["clothing_textile"])

    # Clean up prior demo entities first
    cleanup_demo_workforce(db, business_id)

    created_roles = []
    for r_data in data_template["roles"]:
        role = RoleProfile(
            id=str(uuid.uuid4()),
            business_id=business_id,
            role_name=f"[DEMO DATA] {r_data['role_name']}",
            department=r_data["department"],
            required_skills=r_data["required_skills"],
            optional_skills=r_data.get("optional_skills", []),
            is_demo=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(role)
        created_roles.append(role)

    db.flush()

    created_employees = []
    for emp_data in data_template["employees"]:
        emp = EmployeeProfile(
            id=str(uuid.uuid4()),
            business_id=business_id,
            employee_reference=f"[DEMO DATA] {emp_data['employee_reference']}",
            role=f"[DEMO DATA] {emp_data['role']}",
            department=emp_data["department"],
            experience_years=emp_data["experience_years"],
            current_skills=emp_data["current_skills"],
            preferred_learning_areas=emp_data.get("preferred_learning_areas", []),
            employment_status="Active",
            accessibility_preferences=emp_data.get("accessibility_preferences", []),
            is_demo=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(emp)
        created_employees.append(emp)

    db.commit()

    # Automatically run deterministic skill-gap detection and learning path generation
    detected_gaps = WorkforceIntelligenceService.detect_and_sync_skill_gaps(db, business_id)

    created_paths = []
    for emp in created_employees:
        lp = WorkforceIntelligenceService.generate_or_sync_learning_path(db, business_id, emp.id)
        if lp:
            created_paths.append(lp)

    return {
        "status": "SEEDED",
        "business_id": business_id,
        "roles_seeded": len(created_roles),
        "employees_seeded": len(created_employees),
        "skill_gaps_detected": len(detected_gaps),
        "learning_paths_created": len(created_paths)
    }


def cleanup_demo_workforce(db: Session, business_id: str) -> int:
    """
    Safely removes all is_demo=True workforce records for the given business.
    """
    paths_del = db.query(LearningPath).filter(
        LearningPath.business_id == business_id,
        LearningPath.is_demo == True
    ).delete(synchronize_session=False)

    gaps_del = db.query(SkillGap).filter(
        SkillGap.business_id == business_id,
        SkillGap.is_demo == True
    ).delete(synchronize_session=False)

    emps_del = db.query(EmployeeProfile).filter(
        EmployeeProfile.business_id == business_id,
        EmployeeProfile.is_demo == True
    ).delete(synchronize_session=False)

    roles_del = db.query(RoleProfile).filter(
        RoleProfile.business_id == business_id,
        RoleProfile.is_demo == True
    ).delete(synchronize_session=False)

    db.commit()
    return paths_del + gaps_del + emps_del + roles_del
