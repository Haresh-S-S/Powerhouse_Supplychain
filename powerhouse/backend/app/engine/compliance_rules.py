from typing import List, Dict, Any


def generate_compliance_tasks(profile: Any, approvals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    approval_names = {a["name"] for a in approvals}
    tasks = []

    # 1. Restaurant Specific Tasks
    if "FSSAI Registration / Licence" in approval_names:
        tasks.append({
            "title": "FSSAI Hygiene Audit & FoSTaC Supervisor Training",
            "description": "Appoint certified Food Safety Supervisor under FoSTaC and implement HACCP-based hygiene checklist.",
            "category": "Food Safety",
            "priority": "High",
            "status": "In Progress",
            "due_date": "Due in 5 days",
            "estimated_days": 5,
            "assignee": "Restaurant Manager"
        })
        tasks.append({
            "title": "Potable Water & Ice Quality Laboratory Testing",
            "description": "Six-monthly microbiological and chemical testing of kitchen cooking water from NABL accredited lab.",
            "category": "Food Safety",
            "priority": "Medium",
            "status": "Upcoming",
            "due_date": "Due in 25 days",
            "estimated_days": 25,
            "assignee": "Executive Chef"
        })

    if "Health Trade Licence" in approval_names:
        tasks.append({
            "title": "Commercial Pest Control & Deep Sanitation Log",
            "description": "Conduct licensed pest eradication treatment across food storage, dry pantry, and dining area.",
            "category": "Hygiene & Sanitation",
            "priority": "High",
            "status": "Upcoming",
            "due_date": "Due in 10 days",
            "estimated_days": 10,
            "assignee": "Sanitation In-charge"
        })

    if "Eating House Licence" in approval_names:
        tasks.append({
            "title": "Eating House Police Clearance & Seating Layout Verification",
            "description": "Submit updated seating plan and local police station character certificates for key personnel.",
            "category": "Statutory Licensing",
            "priority": "Medium",
            "status": "Upcoming",
            "due_date": "Due in 20 days",
            "estimated_days": 20,
            "assignee": "Operations Head"
        })

    if "Fire Safety NOC (Kitchen / Dining)" in approval_names:
        tasks.append({
            "title": "Commercial Kitchen Exhaust Duct Degreasing & Hood Audit",
            "description": "Certified mechanical cleaning and degreasing of kitchen canopy filters and exhaust blower ducts.",
            "category": "Safety",
            "priority": "High",
            "status": "Upcoming",
            "due_date": "Due in 8 days",
            "estimated_days": 8,
            "assignee": "Safety Officer"
        })

    # 2. Textile Specific Tasks
    if "State Pollution Control Board Consent (Air & Water / ETP)" in approval_names:
        tasks.append({
            "title": "Quarterly Effluent Quality Log & Solid Waste Record",
            "description": "Maintain environmental compliance manifest and zero liquid discharge inspection logs for textile storage.",
            "category": "Environmental",
            "priority": "High",
            "status": "Upcoming",
            "due_date": "Due in 15 days",
            "estimated_days": 15,
            "assignee": "EHS Lead"
        })

    if "Textile Committee / Ministry of Textiles Compliance" in approval_names:
        tasks.append({
            "title": "Textile Committee Monthly Statistical Production Return",
            "description": "Submit monthly yarn consumption, fabric procurement, and sales data on Ministry of Textiles portal.",
            "category": "Statutory Filing",
            "priority": "Medium",
            "status": "Upcoming",
            "due_date": "Due in 12 days",
            "estimated_days": 12,
            "assignee": "Compliance Manager"
        })

    # 3. Jewellery Specific Tasks
    if "BIS Hallmarking Registration" in approval_names:
        tasks.append({
            "title": "Annual BIS Hallmarking Assaying Reconciliation & HUID Log",
            "description": "Audit laser-inscribed 6-digit Hallmarking Unique Identification (HUID) tags against BIS portal records.",
            "category": "Quality Certification",
            "priority": "High",
            "status": "In Progress",
            "due_date": "Due in 7 days",
            "estimated_days": 7,
            "assignee": "Inventory Head"
        })

    if "PMLA FIU-IND Reporting Registration" in approval_names:
        tasks.append({
            "title": "PMLA Cash Transaction Reporting (CTR) & High-Value KYC Audit",
            "description": "Review monthly customer KYC records and submit Form CTR for any cash transactions exceeding ₹2 Lakhs.",
            "category": "Statutory Finance",
            "priority": "High",
            "status": "Upcoming",
            "due_date": "Due in 10 days",
            "estimated_days": 10,
            "assignee": "Principal Officer"
        })
        tasks.append({
            "title": "Strong Room / Vault Dual-Lock Alarm & CCTV Archive Verification",
            "description": "Verify 90-day mandatory video retention and high-security vault dual-combination access registers.",
            "category": "Security Compliance",
            "priority": "Medium",
            "status": "Upcoming",
            "due_date": "Due in 18 days",
            "estimated_days": 18,
            "assignee": "Security In-charge"
        })

    # 4. Retail Specific Tasks
    if "Legal Metrology (Weights & Measures) Packaged Commodities Registration" in approval_names:
        tasks.append({
            "title": "Annual Legal Metrology Weighing Scale Stamping & Verification",
            "description": "Schedule mandatory annual verification of electronic counter scales by Legal Metrology Inspector.",
            "category": "Statutory Standards",
            "priority": "High",
            "status": "Upcoming",
            "due_date": "Due in 14 days",
            "estimated_days": 14,
            "assignee": "Store Manager"
        })
        tasks.append({
            "title": "LMPC Packaged Commodity Label & MRP Compliance Audit",
            "description": "Verify pre-packaged retail commodities conform to Legal Metrology declaration standards (MRP, Net Qty, Origin).",
            "category": "Consumer Protection",
            "priority": "Medium",
            "status": "Upcoming",
            "due_date": "Due in 22 days",
            "estimated_days": 22,
            "assignee": "Quality Supervisor"
        })

    # 5. Factory / Manufacturing Tasks
    if "Factory License" in approval_names:
        tasks.append({
            "title": "Annual Factory Compliance Report (Form 21)",
            "description": "Consolidated submission of annual production hours, worker safety logs, and machine maintenance records.",
            "category": "Statutory Filing",
            "priority": "High",
            "status": "Upcoming",
            "due_date": "Due in 7 days",
            "estimated_days": 7,
            "assignee": "Arjun Mehta (Compliance Officer)"
        })
        tasks.append({
            "title": "Machinery Guarding & Safety Audit",
            "description": "Onsite inspection of mechanical interlocks, emergency stop switches, and worker PPE compliance.",
            "category": "Safety",
            "priority": "Medium",
            "status": "Upcoming",
            "due_date": "Due in 18 days",
            "estimated_days": 18,
            "assignee": "Capt. R. Sharma (Safety Officer)"
        })

    if "Pollution Control NOC (CTO)" in approval_names:
        tasks.append({
            "title": "Hazardous Waste Management Compliance Manifest",
            "description": "Hazardous solid waste manifest verification and electronic transfer log to authorized recycler.",
            "category": "Environmental",
            "priority": "High",
            "status": "Upcoming",
            "due_date": "Due in 12 days",
            "estimated_days": 12,
            "assignee": "Dr. Sunita Rao (EHS Manager)"
        })
        tasks.append({
            "title": "Quarterly Stack Emission & Flue Gas Analysis",
            "description": "Ambient air quality index sampling and chimney emissions laboratory testing report.",
            "category": "Environmental",
            "priority": "High",
            "status": "Upcoming",
            "due_date": "Due in 30 days",
            "estimated_days": 30,
            "assignee": "Dr. Sunita Rao (EHS Manager)"
        })

    if "Fire Safety Certificate (Industrial)" in approval_names or "Fire Safety Certificate" in approval_names:
        tasks.append({
            "title": "Fire Extinguisher & Hydrant System Pressure Test",
            "description": "Quarterly pressure testing of fire water hydrants, hose reels, and extinguisher replenishment.",
            "category": "Safety",
            "priority": "High",
            "status": "In Progress",
            "due_date": "Scheduled in 4 days",
            "estimated_days": 4,
            "assignee": "Safety Officer"
        })

    if "Electricity Connection Approval (HT)" in approval_names:
        tasks.append({
            "title": "Substation Transformer Inspection & Earthing Test",
            "description": "Earthing resistance measurement and dielectric oil strength testing for industrial power substation.",
            "category": "Utilities",
            "priority": "Medium",
            "status": "Upcoming",
            "due_date": "Due in 22 days",
            "estimated_days": 22,
            "assignee": "Chief Engineer"
        })

    # 6. Common General Compliance Tasks
    if "Shop & Establishment Registration" in approval_names or "Shops & Establishments Registration" in approval_names:
        tasks.append({
            "title": "Annual Shops & Establishments Register Maintenance",
            "description": "Maintain statutory employee muster roll, working hours register, and leave wage records on premises.",
            "category": "Labour & Employment",
            "priority": "High",
            "status": "Upcoming",
            "due_date": "Due in 16 days",
            "estimated_days": 16,
            "assignee": "HR In-charge"
        })

    if "GST Registration & Compliance" in approval_names:
        tasks.append({
            "title": "Monthly GSTR-3B Return Filing & ITC Reconciliation",
            "description": "Summary return of outward taxable supplies, input tax credit claimed, and electronic tax liability payment.",
            "category": "Taxation",
            "priority": "High",
            "status": "Upcoming",
            "due_date": "Due in 15 days",
            "estimated_days": 15,
            "assignee": "Finance Officer"
        })

    if "Employees ESI Registration" in approval_names:
        tasks.append({
            "title": "Employees ESI Pehchan Card Distribution",
            "description": "Generation and biometric distribution of insurance smart cards for newly onboarded staff.",
            "category": "HR & Benefits",
            "priority": "Medium",
            "status": "Completed",
            "due_date": "Completed on schedule",
            "estimated_days": 0,
            "assignee": "Rahul Varma (HR Lead)"
        })

    if "Employees PF Registration" in approval_names:
        tasks.append({
            "title": "Monthly PF Electronic Challan Return (ECR)",
            "description": "Monthly electronic challan upload and payment for employee provident fund contribution.",
            "category": "Statutory Filing",
            "priority": "Medium",
            "status": "Upcoming",
            "due_date": "Due in 25 days",
            "estimated_days": 25,
            "assignee": "Kavita Nair (Finance Officer)"
        })

    return tasks
