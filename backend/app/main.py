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

from pathlib import Path
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Static frontend serving when compiled (enables 100% free single-service Render deployment)
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if not FRONTEND_DIST.exists():
    FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="static_assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend_spa(full_path: str):
        if full_path.startswith("api") or full_path in ["health", "docs", "redoc", "openapi.json"]:
            raise HTTPException(status_code=404, detail="Resource not found")
        file_path = FRONTEND_DIST / full_path
        if full_path and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_DIST / "index.html"))
else:
    @app.get("/", tags=["System"])
    def root():
        """Root endpoint providing quick navigation links."""
        return {
            "message": "Welcome to AIONOS ResolveIT API",
            "health_check": "/health",
            "system_info": "/api/info",
            "documentation": "/docs"
        }

