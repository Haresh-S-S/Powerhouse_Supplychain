import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.router import api_router
from app.core.port_guard import check_and_guard_port

# Configure structured logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("powerhouse")

# Pre-flight port guard check when run under uvicorn server directly
if "uvicorn" in sys.modules and not ("pytest" in sys.modules or os.getenv("TESTING") == "true"):
    check_and_guard_port(host="127.0.0.1", port=8000)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lifespan startup check
    if not ("pytest" in sys.modules or os.getenv("TESTING") == "true"):
        check_and_guard_port(host="127.0.0.1", port=8000)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise Business Compliance & Statutory Approval Management API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Configuration
origins = settings.BACKEND_CORS_ORIGINS
if isinstance(origins, str):
    origins = [o.strip() for o in origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "power-house-api"
    }


# Include Master API Router under /api/v1
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception at {request.url.path}: {str(exc)}", exc_info=settings.DEBUG)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred. Please contact compliance support.",
            "error_code": "INTERNAL_SERVER_ERROR",
        },
    )


if __name__ == "__main__":
    import uvicorn
    if check_and_guard_port(host="127.0.0.1", port=8000):
        uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
