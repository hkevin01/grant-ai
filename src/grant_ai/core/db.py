"""
SQLAlchemy database setup for Grant AI.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/grants.db")

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_session():
    """Get a database session."""
    return SessionLocal()


def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)
