# backend/app/models.py
import os
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Numeric, ForeignKey,
    CheckConstraint, func, Text
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.exc import OperationalError

from pydantic import BaseModel, EmailStr, validator
from passlib.context import CryptContext

# ===============================
# Database setup
# ===============================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./dev.db"
)

engine = create_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()

# ===============================
# Password hashing
# ===============================
bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ===============================
# User ORM model
# ===============================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    age = Column(Integer, nullable=False)

    phone = Column(String(20), unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)

    password_hash = Column(String(255), nullable=False)

    role = Column(String(20), nullable=False, default="user")

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("age >= 20", name="age_min_20"),
        CheckConstraint("role IN ('user','admin')", name="role_allowed"),
    )

    # ให้ main.py เรียกได้ เช่น bcrypt.verify
    bcrypt = bcrypt

# ===============================
# Credit ORM model (Balance table)
# ===============================
class Credit(Base):
    __tablename__ = "credit"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    balance = Column(Numeric(15, 2), nullable=False, default=0.00)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("balance >= 0", name="balance_non_negative"),
    )

# ===============================
# Reports ORM model (Report submissions)
# ===============================
class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)  # Using Text for long descriptions
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", backref="reports")

    __table_args__ = (
        CheckConstraint("category IN ('technical','payment','account','betting','suggestion','other')", name="category_allowed"),
        CheckConstraint("status IN ('pending','reviewing','resolved','closed')", name="status_allowed"),
    )

# ===============================
# Game1 ORM model (Game play tracking)
# ===============================
class Game1(Base):
    __tablename__ = "game1"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Foreign key ไปยัง users table
    bet_amount = Column(Numeric(10, 2), nullable=False)  # ใช้ Numeric สำหรับเงิน
    selected_color = Column(String(10), nullable=False)  # "blue" หรือ "white"
    result_color = Column(String(10), nullable=False)   # ผลลัพธ์จากล้อ
    won = Column(Integer, nullable=False)               # 1 = ชนะ, 0 = แพ้
    win_loss_amount = Column(Numeric(10, 2), nullable=False)  # จำนวนที่ชนะ/แพ้ (+100, -100)
    balance_before = Column(Numeric(10, 2), nullable=False)   # ยอดเงินก่อนเล่น
    balance_after = Column(Numeric(10, 2), nullable=False)    # ยอดเงินหลังเล่น
    played_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship
    user = relationship("User", backref="game1_plays")

    __table_args__ = (
        CheckConstraint("selected_color IN ('blue','white')", name="selected_color_allowed"),
        CheckConstraint("result_color IN ('blue','white')", name="result_color_allowed"),
        CheckConstraint("won IN (0,1)", name="won_boolean"),
        CheckConstraint("bet_amount > 0", name="bet_amount_positive"),
    )

# ===============================
# Game1 Statistics ORM model (จำนวนครั้งที่เล่น)
# ===============================
class Game1Stats(Base):
    __tablename__ = "game1_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    total_games_played = Column(Integer, nullable=False, default=0)  # จำนวนเกมที่เล่นทั้งหมด
    total_wins = Column(Integer, nullable=False, default=0)          # จำนวนครั้งที่ชนะ
    total_losses = Column(Integer, nullable=False, default=0)        # จำนวนครั้งที่แพ้
    total_bet_amount = Column(Numeric(15, 2), nullable=False, default=0.00)    # ยอดเดิมพันรวม
    total_win_amount = Column(Numeric(15, 2), nullable=False, default=0.00)    # ยอดเงินที่ชนะรวม
    total_loss_amount = Column(Numeric(15, 2), nullable=False, default=0.00)   # ยอดเงินที่แพ้รวม
    net_profit_loss = Column(Numeric(15, 2), nullable=False, default=0.00)     # กำไร/ขาดทุนสุทธิ
    first_played_at = Column(DateTime, nullable=True)               # วันที่เล่นครั้งแรก
    last_played_at = Column(DateTime, nullable=True)                # วันที่เล่นครั้งล่าสุด
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", backref="game1_stats")

# ===============================
# Game2 ORM model (Rock Paper Scissors game play tracking)
# ===============================
class Game2(Base):
    __tablename__ = "game2"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Foreign key ไปยัง users table
    bet_amount = Column(Numeric(10, 2), nullable=False)  # จำนวนเงินที่เดิมพัน
    player_choice = Column(String(10), nullable=False)  # "rock", "paper", "scissors"
    bot_choice = Column(String(10), nullable=False)     # "rock", "paper", "scissors"
    result = Column(String(10), nullable=False)         # "win", "lose", "tie"
    win_loss_amount = Column(Numeric(10, 2), nullable=False)  # จำนวนที่ชนะ/แพ้ (+100, -100, 0)
    balance_before = Column(Numeric(10, 2), nullable=False)   # ยอดเงินก่อนเล่น
    balance_after = Column(Numeric(10, 2), nullable=False)    # ยอดเงินหลังเล่น
    played_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship
    user = relationship("User", backref="game2_plays")

    __table_args__ = (
        CheckConstraint("player_choice IN ('rock','paper','scissors')", name="player_choice_allowed"),
        CheckConstraint("bot_choice IN ('rock','paper','scissors')", name="bot_choice_allowed"),
        CheckConstraint("result IN ('win','lose','tie')", name="result_allowed"),
        CheckConstraint("bet_amount > 0", name="bet_amount_positive"),
    )

# ===============================
# Game2 Statistics ORM model (จำนวนครั้งที่เล่น Rock Paper Scissors)
# ===============================
class Game2Stats(Base):
    __tablename__ = "game2_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    total_games_played = Column(Integer, nullable=False, default=0)  # จำนวนเกมที่เล่นทั้งหมด
    total_wins = Column(Integer, nullable=False, default=0)          # จำนวนครั้งที่ชนะ
    total_losses = Column(Integer, nullable=False, default=0)        # จำนวนครั้งที่แพ้
    total_ties = Column(Integer, nullable=False, default=0)          # จำนวนครั้งที่เสมอ
    total_bet_amount = Column(Numeric(15, 2), nullable=False, default=0.00)    # ยอดเดิมพันรวม
    total_win_amount = Column(Numeric(15, 2), nullable=False, default=0.00)    # ยอดเงินที่ชนะรวม
    total_loss_amount = Column(Numeric(15, 2), nullable=False, default=0.00)   # ยอดเงินที่แพ้รวม
    net_profit_loss = Column(Numeric(15, 2), nullable=False, default=0.00)     # กำไร/ขาดทุนสุทธิ
    # สถิติตามตัวเลือก
    rock_played = Column(Integer, nullable=False, default=0)         # จำนวนครั้งที่เลือก Rock
    paper_played = Column(Integer, nullable=False, default=0)        # จำนวนครั้งที่เลือก Paper
    scissors_played = Column(Integer, nullable=False, default=0)     # จำนวนครั้งที่เลือก Scissors
    first_played_at = Column(DateTime, nullable=True)               # วันที่เล่นครั้งแรก
    last_played_at = Column(DateTime, nullable=True)                # วันที่เล่นครั้งล่าสุด
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", backref="game2_stats")

# ===============================
# Create DB
# ===============================
def create_db():
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError:
        raise

# ===============================
# Pydantic schemas (ใช้ validate input)
# ===============================
class RegisterPayload(BaseModel):
    full_name: str
    age: int
    phone: str
    email: EmailStr
    password: str
    confirm_password: str
    agree: bool

    @validator("email")
    def email_must_end_with_gmail(cls, v):
        if not v.endswith("@gmail.com"):
            raise ValueError("Email must end with @gmail.com")
        return v

    @validator("age")
    def age_must_be_20(cls, v):
        if v < 20:
            raise ValueError("Age must be at least 20")
        return v

    @validator("phone")
    def phone_must_be_10_digits(cls, v):
        if not v.startswith("0") or len(v) != 10:
            raise ValueError("Phone number must start with 0 and have exactly 10 digits")
        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

    @validator("agree")
    def must_agree_terms(cls, v):
        if v is not True:
            raise ValueError("You must agree to Terms & Privacy")
        return v

# ===============================
# Ensure Admin user
# ===============================
def ensure_admin(session):
    admin_email = os.getenv("ADMIN_EMAIL", "admin@xbet.com").lower()
    admin_phone = "0000000000"
    
    # Check if admin already exists by email OR phone
    existing_admin = session.query(User).filter(
        (func.lower(User.email) == admin_email) | 
        (User.phone == admin_phone)
    ).first()
    
    if not existing_admin:
        admin = User(
            full_name="Admin",
            age=30,
            phone=admin_phone,
            email=admin_email,
            password_hash=bcrypt.hash("admin123"),
            role="admin",
        )
        session.add(admin)
        session.commit()
        
        # สร้าง Credit (Balance) สำหรับ Admin
        admin_credit = Credit(
            user_id=admin.id,
            balance=1000000.00  # ให้ Admin มี balance เริ่มต้น 1,000,000
        )
        session.add(admin_credit)
        session.commit()
        print(f"✅ Admin user created: {admin_email}")
    
    # เพิ่ม test user ธรรมดา
    test_email = "user@test.com"
    test_phone = "0811111111"
    
    existing_user = session.query(User).filter(
        (func.lower(User.email) == test_email) | 
        (User.phone == test_phone)
    ).first()
    
    if not existing_user:
        test_user = User(
            full_name="Test User",
            age=25,
            phone=test_phone,
            email=test_email,
            password_hash=bcrypt.hash("123456"),
            role="user",
        )
        session.add(test_user)
        session.commit()
        
        # สร้าง Credit (Balance) สำหรับ Test User
        user_credit = Credit(
            user_id=test_user.id,
            balance=0.00  # ให้ Test User มี balance เริ่มต้น 0.00
        )
        session.add(user_credit)
        session.commit()
        print(f"✅ Test user created: {test_email}")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./dev.db"   # ใช้ SQLite ไฟล์ local
)