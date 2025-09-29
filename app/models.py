# app/models.py
from __future__ import annotations
import os
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator, root_validator
from sqlalchemy import (Column, Integer, String, DateTime, CheckConstraint, create_engine, func)
from sqlalchemy.orm import declarative_base, sessionmaker
from passlib.hash import bcrypt


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/acpdb",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(120), nullable=False)
    age = Column(Integer, nullable=False)

    phone = Column(String(20), nullable=False, unique=True, index=True)
    # เก็บอีเมลเป็น lower เสมอ (ทำใน validator ของ Pydantic ตอนรับข้อมูล + ระหว่าง seed)
    email = Column(String(255), nullable=False, unique=True, index=True)

    password_hash = Column(String(255), nullable=False)

    # จำกัดค่า role ให้เป็น 'user' หรือ 'admin' เท่านั้น
    role = Column(String(16), nullable=False, default="user")

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("age >= 0", name="age_non_negative"),
        CheckConstraint("role IN ('user','admin')", name="role_allowed"),
    )

def create_db() -> None:
    """สร้างตาราง (ถ้ายังไม่มี)"""
    Base.metadata.create_all(bind=engine)
# -------------------------
# Pydantic Schemas
# -------------------------
class RegisterIn(BaseModel):
    full_name: str
    age: int
    phone: str
    email: EmailStr
    password: str
    confirm_password: str
    agree: Optional[bool] = False

    @validator("email")
    def email_must_be_gmail(cls, v: EmailStr) -> EmailStr:
        # บังคับ @gmail.com และ normalize เป็นตัวเล็กเสมอ
        v_str = str(v).strip().lower()
        if not v_str.endswith("@gmail.com"):
            raise ValueError("Email must end with @gmail.com")
        return EmailStr(v_str)

    @validator("age")
    def age_at_least_20(cls, v: int) -> int:
        if v < 20:
            raise ValueError("Age must be at least 20")
        return v

    @validator("phone")
    def phone_must_start_0_and_10_digits(cls, v: str) -> str:
        vv = v.strip()
        import re
        if not re.fullmatch(r"^0\d{9}$", vv):
            raise ValueError("Phone number must start with 0 and have exactly 10 digits")
        return vv

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
# -------------------------
# Helpers
# -------------------------
def hash_password(raw: str) -> str:
    return bcrypt.hash(raw)

def ensure_admin(session: SessionLocal) -> None:
    """
    สร้างแอดมินเริ่มต้นถ้ายังไม่มี (ใช้ตอน dev/test)
    เรียกใช้จาก main.py ใน startup ก็ได้:
        with SessionLocal() as s:
            ensure_admin(s)
    """
    admin_email = os.getenv("ADMIN_EMAIL", "h2w@admin.com").lower()
    u = session.query(User).filter(func.lower(User.email) == admin_email).first()
    if not u:
        u = User(
            full_name="H2W",
            age=25,
            phone="0999999999",
            email=admin_email,
            password_hash=bcrypt.hash("admin123"),
            role="admin",
        )
        session.add(u)
        session.commit()
