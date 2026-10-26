# Sets up the database connection that models.py and crud.py use.

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# Defaults to a local SQLite file (backend/notes.db). To switch to PostgreSQL
# later, just set DATABASE_URL in .env, e.g.:
#   DATABASE_URL=postgresql://user:password@localhost/dbname
# Nothing in models.py or crud.py needs to change — they only use the
# SessionLocal and Base defined here.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./notes.db")

# check_same_thread is a SQLite-only setting (it's ignored by other databases).
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def init_db():
    """Creates the database tables if they don't exist yet, and updates
    existing tables if the models have grown new columns since."""
    from db import models  # imported here so Note registers with Base before create_all
    Base.metadata.create_all(bind=engine)
    _add_missing_columns()


def _add_missing_columns():
    """
    create_all() only creates brand-new tables — it won't add a column to a
    table that already exists. This adds any columns our models have grown
    since an existing notes.db was first created (currently just needs_review),
    so older databases keep working without the user having to delete them.

    Note: the ALTER TABLE syntax here is SQLite-specific. If this project
    switches to PostgreSQL later, this function would need to be adjusted
    (or a proper migration tool like Alembic used instead).
    """
    inspector = inspect(engine)
    if "notes" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("notes")}
    if "needs_review" not in existing_columns:
        with engine.connect() as connection:
            connection.execute(text("ALTER TABLE notes ADD COLUMN needs_review BOOLEAN DEFAULT 0"))
            connection.commit()
