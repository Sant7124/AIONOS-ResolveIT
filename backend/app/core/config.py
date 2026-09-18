from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directories
CORE_DIR = Path(__file__).resolve().parent
APP_DIR = CORE_DIR.parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"

class Settings(BaseSettings):
    APP_NAME: str = "AIONOS ResolveIT API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    # Temporal Simulation Anchoring
    SIMULATION_BASE_DATE: str = "2026-09-21T09:00:00Z"
    
    # AI Provider Options: 'mock', 'openai', 'gemini'
    LLM_PROVIDER: str = "mock"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{BACKEND_DIR}/veridian_it.db"
    
    # Ground Truth Data Paths
    POLICIES_PATH: str = str(DATA_DIR / "policies" / "knowledge_base.json")
    REQUESTS_PATH: str = str(DATA_DIR / "employee_requests" / "requests.json")
    TICKETS_PATH: str = str(DATA_DIR / "tickets" / "seed_tickets.json")

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
