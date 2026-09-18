from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Configure SQLite engine
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """FastAPI dependency for yielding database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all database tables registered on Base and migrate schema changes safely."""
    # Import all models so that Base.metadata knows about them
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # Safe SQLite column migrations for conversations table
    with engine.connect() as conn:
        try:
            result = conn.exec_driver_sql("PRAGMA table_info(conversations)")
            existing_cols = {row[1] for row in result.fetchall()}
            if "active_intent" not in existing_cols:
                conn.exec_driver_sql("ALTER TABLE conversations ADD COLUMN active_intent VARCHAR(100)")
            if "active_category" not in existing_cols:
                conn.exec_driver_sql("ALTER TABLE conversations ADD COLUMN active_category VARCHAR(100)")
            if "pending_question" not in existing_cols:
                conn.exec_driver_sql("ALTER TABLE conversations ADD COLUMN pending_question TEXT")
            if "context_data" not in existing_cols:
                conn.exec_driver_sql("ALTER TABLE conversations ADD COLUMN context_data JSON DEFAULT '{}'")
            conn.commit()
        except Exception:
            pass
