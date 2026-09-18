from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.session import init_db, SessionLocal
from app.database.seed import seed_policies, seed_employee_requests, seed_tickets, seed_initial_audit
from app.models import Policy
from app.api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and seed if database is empty
    init_db()
    db = SessionLocal()
    try:
        if db.query(Policy).count() == 0:
            seed_policies(db)
            seed_employee_requests(db)
            seed_tickets(db)
            seed_initial_audit(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Internal IT Service & Resolution Agent — Grounded in the Authoritative Data Pack",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint to verify backend operational readiness."""
    return {
        "status": "healthy",
        "service": "aionos-resolveit-api",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "simulation_base_date": settings.SIMULATION_BASE_DATE,
        "active_provider": settings.LLM_PROVIDER
    }

@app.get("/", tags=["System"])
def root():
    """Root endpoint providing quick navigation links."""
    return {
        "message": "Welcome to AIONOS ResolveIT API",
        "health_check": "/health",
        "system_info": "/api/info",
        "documentation": "/docs"
    }
