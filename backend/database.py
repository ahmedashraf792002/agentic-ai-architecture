from __future__ import annotations

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

engine = create_engine(os.environ["DATABASE_URL"], future=True)
SessionLocal: sessionmaker = sessionmaker(
    bind=engine, expire_on_commit=False, future=True
)


def get_session() -> Session:
    return SessionLocal()
