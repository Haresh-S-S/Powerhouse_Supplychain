import os
import sys

# Append parent dir so app can be imported
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal
from app.models.business import BusinessProfile
from app.models.application import Application
from app.models.alert import Alert
from app.services.analysis_service import BusinessAnalysisService


def seed_database():
    db = SessionLocal()
    try:
        existing = db.query(BusinessProfile).filter(BusinessProfile.business_name == "Powerhouse Industries").first()
        if existing:
            print(f"[Seed] Business 'Powerhouse Industries' already exists (ID: {existing.id}). Running/verifying analysis...")
            BusinessAnalysisService.run_and_save_analysis(db, existing.id)
            print("[Seed] Existing profile verified and analysis updated successfully.")
            return

        print("[Seed] Creating primary seed profile: Powerhouse Industries...")
        profile = BusinessProfile(
            business_name="Powerhouse Industries",
            business_type="Private Limited Company",
            industry="Manufacturing",
            sector="Industrial Equipment & Machinery",
            established_date="2018-06-15",
            company_size="Medium Enterprise (₹10 Cr - ₹50 Cr)",
            employee_count=85,
            annual_turnover="₹28.5 Crores",
            registered_address="Plot 42, Sector 8, MIDC Industrial Area, Andheri East",
            city="Mumbai",
            state="Maharashtra",
            country="India",
            postal_code="400093",
            primary_activity="Precision industrial valves, actuators, and flow control systems manufacturing.",
            secondary_activities="Contract machining and specialized metallurgical testing.",
            manufacturing_activity=True,
            import_activities=True,
            export_activities=False,
            environmental_impact="Moderate",
            operating_status="Active",
            has_gst=True,
            has_msme_registration=True,
            has_udyam_registration=True,
            cin="U29253MH2018PTC310948",
            pan="AAACP4821K",
            gstin="27AAACP4821K1ZV",
            udyam_number="UDYAM-MH-19-0024891"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        print(f"[Seed] Created BusinessProfile with ID: {profile.id}")

        # Execute and persist initial analysis
        print("[Seed] Running initial deterministic business analysis...")
        analysis = BusinessAnalysisService.run_and_save_analysis(db, profile.id)
        print(f"[Seed] Analysis compiled: {analysis.total_approvals} approvals, {analysis.total_compliance_tasks} tasks, {analysis.total_recommended_schemes} schemes.")

        # Seed sample department applications
        print("[Seed] Seeding sample applications...")
        apps = [
            Application(
                business_profile_id=profile.id,
                application_number="APP-2024-0041",
                department="Directorate of Industries",
                application_name="Factory License Renewal & Expansion",
                status="Under Review",
                submission_date="12 May 2024",
                last_updated="18 May 2024",
                current_stage="Under Review",
                timeline=[
                    {"stage": "Draft Submitted", "date": "12 May 2024", "status": "Completed"},
                    {"stage": "Document Verification", "date": "15 May 2024", "status": "Completed"},
                    {"stage": "On-site Safety Inspection", "date": "18 May 2024", "status": "In Progress"},
                    {"stage": "Final Clearance Issuance", "date": "Pending", "status": "Pending"}
                ]
            ),
            Application(
                business_profile_id=profile.id,
                application_number="APP-2024-0038",
                department="State Pollution Control Board",
                application_name="Consent to Operate (CTO) Renewal",
                status="Submitted",
                submission_date="05 May 2024",
                last_updated="14 May 2024",
                current_stage="Submitted",
                timeline=[
                    {"stage": "Application Lodged", "date": "05 May 2024", "status": "Completed"},
                    {"stage": "Flue Gas Report Review", "date": "14 May 2024", "status": "In Progress"},
                    {"stage": "Board Sanction", "date": "Pending", "status": "Pending"}
                ]
            ),
            Application(
                business_profile_id=profile.id,
                application_number="APP-2024-0012",
                department="State Fire & Emergency Services",
                application_name="Fire NOC Renewal & Hydrant Audit",
                status="Approved",
                submission_date="20 Apr 2024",
                last_updated="02 May 2024",
                current_stage="Approved",
                timeline=[
                    {"stage": "Application Lodged", "date": "20 Apr 2024", "status": "Completed"},
                    {"stage": "Hydrant Pressure Audit", "date": "26 Apr 2024", "status": "Completed"},
                    {"stage": "Certificate Issued", "date": "02 May 2024", "status": "Completed"}
                ]
            )
        ]
        for a in apps:
            db.add(a)

        # Seed sample alerts
        print("[Seed] Seeding sample compliance alerts...")
        alerts = [
            Alert(
                business_profile_id=profile.id,
                title="Pollution Control NOC Renewal Due Soon",
                description="Your Consent to Operate (CTO) expires in 5 days. Ensure stack emission reports are attached.",
                severity="critical",
                category="Environmental",
                is_read=False,
                action_url="/approvals",
                due_date="Due in 5 days"
            ),
            Alert(
                business_profile_id=profile.id,
                title="Fire Hydrant Pressure Test Scheduled",
                description="State Fire Department inspection officer audit scheduled on 02 Jun 2026 at 11:00 AM.",
                severity="upcoming",
                category="Safety",
                is_read=False,
                action_url="/compliance-tasks",
                due_date="In 4 days"
            ),
            Alert(
                business_profile_id=profile.id,
                title="PMEGP Subsidy Tranche Open",
                description="Quarterly application window is open for up to 35% capital equipment subsidy.",
                severity="information",
                category="Government Scheme",
                is_read=False,
                action_url="/government-schemes",
                due_date="Open year-round"
            )
        ]
        for al in alerts:
            db.add(al)

        db.commit()
        print("[Seed] Seeding completed successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
