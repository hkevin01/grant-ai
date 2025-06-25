"""
Script to load grants from JSON and insert into the database using SQLAlchemy ORM.
"""

import json
from pathlib import Path

from sqlalchemy import text

from grant_ai.db import SessionLocal
from grant_ai.models.grant import Grant


def main():
    session = SessionLocal()
    data_path = Path("data/grants_gov_housing.json")
    if not data_path.exists():
        print(f"File not found: {data_path}")
        return
    with open(data_path, "r") as f:
        grants_data = json.load(f)
    count = 0
    for g in grants_data:
        # Upsert by id
        exists = session.execute(text("SELECT 1 FROM grants WHERE id=:id"), {"id": g["id"]}).first()
        if not exists:
            grant = Grant(**g)
            session.add(grant)
            count += 1
    session.commit()
    print(f"Inserted {count} new grants into the database.")
    session.close()


if __name__ == "__main__":
    main()
