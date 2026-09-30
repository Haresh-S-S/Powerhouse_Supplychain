from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.business import BusinessProfile
from app.models.analysis import BusinessAnalysis
from app.models.approval import Approval
from app.models.compliance_task import ComplianceTask
from app.models.document import Document
from app.models.scheme import GovernmentScheme
from app.engine.business_analyzer import analyze_business_profile


class BusinessAnalysisService:
    @staticmethod
    def run_and_save_analysis(db: Session, business_profile_id: str) -> Optional[BusinessAnalysis]:
        profile = db.query(BusinessProfile).filter(BusinessProfile.id == business_profile_id).first()
        if not profile:
            return None

        # Execute rule analysis engine
        analysis_data = analyze_business_profile(profile)
        summary = analysis_data["summary"]

        # Create BusinessAnalysis record
        analysis_record = BusinessAnalysis(
            business_profile_id=profile.id,
            analysis_version="1.0",
            risk_level=analysis_data["risk_level"],
            analysis_status="Completed",
            total_approvals=summary["total_approvals"],
            high_priority_approvals=summary["high_priority_approvals"],
            total_compliance_tasks=summary["total_compliance_tasks"],
            total_required_documents=summary["total_required_documents"],
            total_recommended_schemes=summary["total_recommended_schemes"],
            compliance_score=summary["compliance_score"],
            analysis_result=analysis_data,
            analysis_date=analysis_data["analysis_date"]
        )
        db.add(analysis_record)
        db.flush()

        # Clean existing generated entities for this profile before inserting refreshed items
        db.query(Approval).filter(Approval.business_profile_id == profile.id).delete()
        db.query(ComplianceTask).filter(ComplianceTask.business_profile_id == profile.id).delete()
        db.query(Document).filter(Document.business_profile_id == profile.id).delete()
        db.query(GovernmentScheme).filter(GovernmentScheme.business_profile_id == profile.id).delete()

        # Persist generated approvals
        for a in analysis_data["approvals"]:
            appr = Approval(
                business_profile_id=profile.id,
                analysis_id=analysis_record.id,
                name=a["name"],
                authority=a["authority"],
                category=a["category"],
                description=a.get("description"),
                priority=a.get("priority", "High"),
                status=a.get("status", "Pending"),
                trigger_reason=a.get("trigger_reason"),
                required_documents_count=a.get("required_documents_count", 0),
                progress_percentage=a.get("progress_percentage", 0),
                due_date=a.get("due_date"),
                steps=a.get("steps")
            )
            db.add(appr)

        # Persist generated tasks
        for t in analysis_data["compliance_tasks"]:
            task = ComplianceTask(
                business_profile_id=profile.id,
                title=t["title"],
                description=t.get("description"),
                category=t.get("category", "Statutory Filing"),
                priority=t.get("priority", "High"),
                status=t.get("status", "Upcoming"),
                due_date=t.get("due_date", "Due soon"),
                estimated_days=t.get("estimated_days", 0),
                assignee=t.get("assignee")
            )
            db.add(task)

        # Persist generated documents
        for d in analysis_data["required_documents"]:
            doc = Document(
                business_profile_id=profile.id,
                name=d["name"],
                category=d["category"],
                file_type=d.get("file_type", "PDF"),
                file_size=d.get("file_size"),
                status=d.get("status", "Verified"),
                required=d.get("required", True),
                upload_date=d.get("upload_date"),
                expiry_date=d.get("expiry_date"),
                renewal_cycle=d.get("renewal_cycle")
            )
            db.add(doc)

        # Persist generated schemes
        for s in analysis_data["recommended_schemes"]:
            scheme = GovernmentScheme(
                business_profile_id=profile.id,
                analysis_id=analysis_record.id,
                name=s["name"],
                short_name=s.get("short_name"),
                description=s.get("description"),
                benefit=s["benefit"],
                category=s["category"],
                match_score=s.get("match_score", 0),
                match_reason=s.get("match_reason"),
                eligibility_status=s.get("eligibility_status", "Eligible"),
                official_source=s.get("official_source"),
                deadline=s.get("deadline")
            )
            db.add(scheme)

        db.commit()
        db.refresh(analysis_record)
        return analysis_record

    @staticmethod
    def get_analysis_by_id(db: Session, analysis_id: str) -> Optional[BusinessAnalysis]:
        return db.query(BusinessAnalysis).filter(BusinessAnalysis.id == analysis_id).first()

    @staticmethod
    def get_latest_for_profile(db: Session, business_profile_id: str) -> Optional[BusinessAnalysis]:
        return (
            db.query(BusinessAnalysis)
            .filter(BusinessAnalysis.business_profile_id == business_profile_id)
            .order_by(BusinessAnalysis.created_at.desc())
            .first()
        )
