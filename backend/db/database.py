# Sets up the database connection that models.py and crud.py use.

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
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
    """Creates the database tables if they don't exist yet."""
    from db import models  # imported here so Note registers with Base before create_all
    Base.metadata.create_all(bind=engine)
