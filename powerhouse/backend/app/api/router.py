from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.business import router as business_router
from app.api.analysis import router as analysis_router
from app.api.approvals import router as approvals_router
from app.api.tasks import router as tasks_router
from app.api.documents import router as documents_router
from app.api.applications import router as applications_router
from app.api.schemes import router as schemes_router
from app.api.alerts import router as alerts_router
from app.api.proposals import router as proposals_router
from app.api.audit import router as audit_router
from app.api.compare import router as compare_router
from app.api.demo import router as demo_router
from app.api.rag import router as rag_router
from app.api.green import router as green_router
from app.api.supply_chain import router as supply_chain_router
from app.api.workforce import router as workforce_router
from app.workforce_ai.router import router as workforce_ai_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(business_router)
api_router.include_router(analysis_router)
api_router.include_router(approvals_router)
api_router.include_router(tasks_router)
api_router.include_router(documents_router)
api_router.include_router(applications_router)
api_router.include_router(schemes_router)
api_router.include_router(alerts_router)
api_router.include_router(proposals_router)
api_router.include_router(audit_router)
api_router.include_router(compare_router)
api_router.include_router(demo_router)
api_router.include_router(rag_router)
api_router.include_router(green_router)
api_router.include_router(supply_chain_router)
api_router.include_router(workforce_router)
# Workforce AI Intelligence – additive, does not modify existing workforce routes
api_router.include_router(workforce_ai_router)
# Supply Chain AI Intelligence – additive, control tower architecture
from app.supply_chain_ai.router import router as supply_chain_ai_router
api_router.include_router(supply_chain_ai_router)


