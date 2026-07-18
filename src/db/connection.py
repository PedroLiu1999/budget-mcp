import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///budget.db")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def set_engine(new_engine):
    """Utility function to override database engine (e.g. for testing)."""
    global engine, SessionLocal
    engine = new_engine
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Ensure database tables exist using SQLAlchemy metadata."""
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_session():
    """Provide a transactional scope around database operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
