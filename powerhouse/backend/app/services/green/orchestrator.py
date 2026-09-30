import uuid
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.business import BusinessProfile
from app.models.green_opportunity import GreenOpportunity
from app.models.agent_run import AgentRun
from app.models.green_impact import GreenImpactMeasurement
from app.services.green.agents import GreenComputingAgent, EnergyAgent, ResourceWasteAgent
from app.services.green.emission_factors import EmissionFactorService


class GreenAgentOrchestrator:
    """
    Real Agentic Orchestration Service for Green Industry Flow AI.
    Executes the complete lifecycle:
    OBSERVE -> RETRIEVE -> DETECT -> ANALYZE -> REASON -> RECOMMEND -> VALIDATE -> PERSIST/PROPOSE
    """

    @staticmethod
    def run_orchestration(db: Session, profile: BusinessProfile) -> Dict[str, Any]:
        start_overall = time.perf_counter()
        run_id = str(uuid.uuid4())
        trace_steps = []
        input_sources = ["BUSINESS_PROFILE", "COMPLIANCE_TASKS", "DOCUMENTS_VAULT"]

        # Ensure verified emission factors exist
        EmissionFactorService.ensure_default_factors(db)

        # ----------------------------------------------------------------
        # Stage 1: OBSERVE
        # ----------------------------------------------------------------
        s1_start = time.perf_counter()
        agents = [
            GreenComputingAgent(),
            EnergyAgent(),
            ResourceWasteAgent(),
        ]
        all_observations = {}
        for agent in agents:
            obs = agent.observe(db, profile)
            all_observations[agent.agent_name] = obs
            if obs.get("has_metrics") or obs.get("has_energy_data"):
                input_sources.append(agent.agent_name)

        s1_duration = int((time.perf_counter() - s1_start) * 1000)
        trace_steps.append({
            "step": "Observe",
            "status": "COMPLETED",
            "duration_ms": s1_duration,
            "source_count": len(input_sources),
            "summary": f"Observed operational telemetry across {len(agents)} specialized agents."
        })

        # ----------------------------------------------------------------
        # Stage 2: RETRIEVE
        # ----------------------------------------------------------------
        s2_start = time.perf_counter()
        # Retrieve verified statutory emission factors and business category context
        factors = EmissionFactorService.get_all_factors(db)
        category = profile.business_category or profile.industry or "manufacturing"
        s2_duration = int((time.perf_counter() - s2_start) * 1000)
        trace_steps.append({
            "step": "Retrieve",
            "status": "COMPLETED",
            "duration_ms": s2_duration,
            "source_count": len(factors),
            "summary": f"Retrieved {len(factors)} verified statutory emission factors for category: {category}."
        })

        # ----------------------------------------------------------------
        # Stage 3: DETECT
        # ----------------------------------------------------------------
        s3_start = time.perf_counter()
        all_detections = []
        for agent in agents:
            obs = all_observations[agent.agent_name]
            dets = agent.detect(obs)
            for d in dets:
                d["_agent"] = agent
            all_detections.extend(dets)

        s3_duration = int((time.perf_counter() - s3_start) * 1000)
        trace_steps.append({
            "step": "Detect",
            "status": "COMPLETED",
            "duration_ms": s3_duration,
            "source_count": len(all_detections),
            "summary": f"Detected {len(all_detections)} distinct sustainability patterns and inefficiencies."
        })

        # ----------------------------------------------------------------
        # Stage 4: ANALYZE
        # ----------------------------------------------------------------
        s4_start = time.perf_counter()
        raw_recommendations = []
        for agent in agents:
            agent_dets = [d for d in all_detections if d.get("_agent") == agent]
            if agent_dets:
                recs = agent.analyze(db, agent_dets)
                raw_recommendations.extend(recs)

        s4_duration = int((time.perf_counter() - s4_start) * 1000)
        trace_steps.append({
            "step": "Analyze",
            "status": "COMPLETED",
            "duration_ms": s4_duration,
            "source_count": len(raw_recommendations),
            "summary": f"Computed deterministic energy, financial, and carbon impacts for {len(raw_recommendations)} recommendations."
        })

        # ----------------------------------------------------------------
        # Stage 5 & 6: REASON & RECOMMEND
        # ----------------------------------------------------------------
        s5_start = time.perf_counter()
        # Rank opportunities deterministically: Priority (High=3, Med=2, Low=1) + Confidence
        priority_weights = {"High": 30, "Medium": 20, "Low": 10}
        ranked_recs = sorted(
            raw_recommendations,
            key=lambda r: (priority_weights.get(r["priority"], 10) + r["confidence"] * 10),
            reverse=True
        )
        s5_duration = int((time.perf_counter() - s5_start) * 1000)
        trace_steps.append({
            "step": "Reason & Recommend",
            "status": "COMPLETED",
            "duration_ms": s5_duration,
            "source_count": len(ranked_recs),
            "summary": f"Structured and prioritized {len(ranked_recs)} evidence-backed green opportunities."
        })

        # ----------------------------------------------------------------
        # Stage 7: VALIDATE (Policy Gate)
        # ----------------------------------------------------------------
        s7_start = time.perf_counter()
        validated_count = sum(1 for r in ranked_recs if r["policy_status"] in ["PASS", "REVIEW_REQUIRED"])
        s7_duration = int((time.perf_counter() - s7_start) * 1000)
        trace_steps.append({
            "step": "Validate",
            "status": "COMPLETED",
            "duration_ms": s7_duration,
            "source_count": validated_count,
            "summary": f"Validated all recommendations against operational safety rules and production freeze windows."
        })

        # ----------------------------------------------------------------
        # Stage 8: PERSIST
        # ----------------------------------------------------------------
        created_opportunities = []
        for rec in ranked_recs:
            # Check if this exact recommendation already exists to prevent duplicate spam
            existing = (
                db.query(GreenOpportunity)
                .filter(
                    GreenOpportunity.business_profile_id == profile.id,
                    GreenOpportunity.title == rec["title"],
                    GreenOpportunity.status.in_(["DETECTED", "UNDER_REVIEW", "APPROVED", "TASK_CREATED"]),
                )
                .first()
            )
            if existing:
                # Update existing record
                existing.estimated_cost_impact = rec["estimated_cost_impact"]
                existing.estimated_energy_impact = rec["estimated_energy_impact"]
                existing.estimated_carbon_impact = rec["estimated_carbon_impact"]
                existing.evidence = rec["evidence"]
                existing.confidence = rec["confidence"]
                existing.policy_status = rec["policy_status"]
                existing.policy_notes = rec["policy_notes"]
                created_opportunities.append(existing)
            else:
                opp = GreenOpportunity(
                    id=str(uuid.uuid4()),
                    business_profile_id=profile.id,
                    agent_type=rec["agent_type"],
                    title=rec["title"],
                    category=rec["category"],
                    priority=rec["priority"],
                    severity=rec["severity"],
                    detected_issue=rec["detected_issue"],
                    evidence=rec["evidence"],
                    cause=rec["cause"],
                    recommended_action=rec["recommended_action"],
                    estimated_cost_impact=rec["estimated_cost_impact"],
                    estimated_energy_impact=rec["estimated_energy_impact"],
                    estimated_carbon_impact=rec["estimated_carbon_impact"],
                    implementation_effort=rec["implementation_effort"],
                    confidence=rec["confidence"],
                    status="DETECTED",
                    policy_status=rec["policy_status"],
                    policy_notes=rec["policy_notes"],
                )
                db.add(opp)
                db.flush()

                # Also create an initial baseline impact measurement if energy or paper metric exists
                if rec.get("estimated_energy_impact") and rec["estimated_energy_impact"].get("baseline_kwh"):
                    base_kwh = rec["estimated_energy_impact"]["baseline_kwh"]
                    impact = GreenImpactMeasurement(
                        id=str(uuid.uuid4()),
                        opportunity_id=opp.id,
                        business_profile_id=profile.id,
                        metric_name="Monthly Energy Consumption",
                        unit="kWh",
                        baseline_value=base_kwh,
                        measured_value=None,  # Impact verification pending
                        is_demo=any(e.get("is_demo") for e in rec["evidence"]),
                        verification_status="PENDING",
                        formula="baseline_kwh - post_action_kwh",
                        assumptions=rec["estimated_energy_impact"].get("assumptions", ""),
                    )
                    db.add(impact)

                created_opportunities.append(opp)

        # Record AgentRun audit trace
        run_record = AgentRun(
            id=run_id,
            business_profile_id=profile.id,
            agent_type="GreenAgentOrchestrator",
            status="COMPLETED" if created_opportunities else "INSUFFICIENT_DATA",
            input_sources=list(set(input_sources)),
            output_count=len(created_opportunities),
            trace_steps=trace_steps,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            model_used="Deterministic Hybrid Rule & Factor Orchestrator",
        )
        db.add(run_record)
        db.commit()
        db.refresh(run_record)

        return {
            "run_id": run_id,
            "status": run_record.status,
            "output_count": len(created_opportunities),
            "trace_steps": trace_steps,
            "opportunities": created_opportunities,
        }
