"""
Initialize the database tables for Grant AI (including the new GrantORM model).
"""
from grant_ai.core.db import Base, engine
from grant_ai.models.grant import GrantORM

if __name__ == "__main__":
    print("Creating all tables...")
    Base.metadata.create_all(engine)
    print("✅ Database tables created.") 