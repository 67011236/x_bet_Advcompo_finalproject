# models.py

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, validator, root_validator
from sqlalchemy import (
    Column, Integer, String, DateTime, CheckConstraint, create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker
from passlib.hash import bcrypt

# ---------- DB setup ----------
DATABASE_URL = "postgresql://postgres:postgres@db:5432/acpdb"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    phone = Column(String(16), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String(16), nullable=False, default="user")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("age >= 0", name="age_non_negative"),
    )

def create_db() -> None:
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

    # รับค่ามาจาก form-data
    @classmethod
    def as_form(
        cls,
        full_name: str,
        age: int,
        phone: str,
        email: str,
        password: str,
        confirm_password: str,
        agree: Optional[bool] = False
    ):
        return cls(
            full_name=full_name,
            age=age,
            phone=phone,
            email=email,
            password=password,
            confirm_password=confirm_password,
            agree=bool(agree),
        )

    @validator("email")
    def email_must_be_gmail(cls, v: EmailStr):
        if not str(v).lower().endswith("@gmail.com"):
            raise ValueError("Email must end with @gmail.com")
        return v

    @validator("age")
    def age_must_be_20up(cls, v: int):
        if v < 20:
            raise ValueError("Age must be at least 20")
        return v

    @validator("phone")
    def phone_format(cls, v: str):
        # ขึ้นต้นด้วย 0 และยาว 10 หลักเท่านั้น
        if not re.fullmatch(r"^0\d{9}$", v.strip()):
            raise ValueError("Phone number must start with 0 and have exactly 10 digits")
        return v

    @root_validator
    def passwords_and_agree(cls, values):
        pwd = values.get("password")
        cpw = values.get("confirm_password")
        agree = values.get("agree")

        if pwd != cpw:
            raise ValueError("Passwords do not match")
        if not agree:
            raise ValueError("You must agree to Terms & Privacy")
        return values


class RegisterOut(BaseModel):
    id: Optional[int] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None

def hash_password(raw: str) -> str:
    return bcrypt.hash(raw)
