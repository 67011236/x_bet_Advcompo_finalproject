import os
import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator
from passlib.hash import bcrypt

from sqlalchemy import (
    Column, Integer, String, DateTime, Text, CheckConstraint, create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker

# ---------- DB ----------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/acpdb"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---------- SQLAlchemy Model ----------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(Text, nullable=False)
    age = Column(Integer, nullable=False)
    phone = Column(String(16), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(Text, nullable=False)
    role = Column(String(16), nullable=False, default="user")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("age >= 0", name="age_non_negative"),
    )

def create_db():
    Base.metadata.create_all(bind=engine)

# ---------- Pydantic Schemas ----------
class RegisterIn(BaseModel):
    full_name: str
    age: int
    phone: str
    email: EmailStr
    password: str
    confirm_password: str
    agree: bool

    @field_validator("email")
    @classmethod
    def email_must_be_gmail(cls, v):
        if not v.endswith("@gmail.com"):
            raise ValueError("Email must end with @gmail.com")
        return v

    @field_validator("age")
    @classmethod
    def age_must_be_20up(cls, v):
        if v < 20:
            raise ValueError("Age must be at least 20")
        return v

    @field_validator("phone")
    @classmethod
    def phone_rule(cls, v):
        if not re.fullmatch(r"0\d{9}", v):
            raise ValueError("Phone must have 10 digits and start with 0")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        pwd = info.data.get("password")
        if not pwd or v != pwd:
            raise ValueError("Passwords do not match")
        return v

    @field_validator("agree")
    @classmethod
    def must_agree(cls, v):
        if not v:
            raise ValueError("You must agree to Terms & Privacy")
        return v

class RegisterOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str

def hash_password(raw: str) -> str:
    return bcrypt.hash(raw)
