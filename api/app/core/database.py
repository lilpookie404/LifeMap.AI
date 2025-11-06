from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
from datetime import datetime
from .config import settings
import json

DATABASE_URL = (
    f"postgresql+psycopg://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)
engine = create_engine(DATABASE_URL, echo=False)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str

class Profile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    academics_json: Optional[str] = None
    career_json: Optional[str] = None
    personal_json: Optional[str] = None

class Roadmap(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    domain: str
    version: int = 1
    plan_json: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Feedback(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    roadmap_id: int = Field(foreign_key="roadmap.id")
    signal_type: str
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

def init_db():
    print("[DB] Creating tables if not exist…")
    SQLModel.metadata.create_all(engine)

def seed_demo():
    with Session(engine) as session:
        existing = session.exec(select(User)).all()
        if existing:
            print("[DB] Demo users already exist.")
            return
        u1 = User(name="Nitesh", email="nitesh@example.com")
        u2 = User(name="Vaishnavi", email="vaishnavi@example.com")
        session.add_all([u1, u2])
        session.commit()
        print("[DB] Seeded demo users:", json.dumps([u1.email, u2.email]))
