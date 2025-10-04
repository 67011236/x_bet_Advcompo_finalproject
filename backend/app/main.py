from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os, re
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal

# import ของคุณเอง
from .models import SessionLocal, User, Details, create_db, ensure_admin

APP_NAME = os.getenv("APP_NAME", "MyApp")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@xbet.com").lower()

app = FastAPI(title=APP_NAME)

# ✅ เปิด CORS ให้ Next.js เรียกได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COOKIE_NAME = "useremail"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def on_startup():
    create_db()
    with SessionLocal() as s:
        ensure_admin(s)


def current_email(request: Request) -> str | None:
    return (request.cookies.get(COOKIE_NAME) or "").lower() or None

def must_login(request: Request):
    if not current_email(request):
        raise HTTPException(status_code=401, detail="Not authenticated")

def must_admin(request: Request):
    email = current_email(request)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if email != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Admin only")

# ---------- Models ----------
class RegisterPayload(BaseModel):
    full_name: str
    age: int
    phone: str
    email: str
    password: str
    confirm_password: str

class LoginPayload(BaseModel):
    email: str
    password: str

class DepositPayload(BaseModel):
    amount: float

class WithdrawPayload(BaseModel):
    amount: float

# ---------- Endpoints ----------
@app.get("/")
def root(request: Request):
    return {"ok": True, "service": "fastapi", "email": current_email(request)}

@app.get("/me")
def me(request: Request, db: Session = Depends(get_db)):
    email = current_email(request)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get user from database to check role
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return {
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_admin": user.role == "admin"
    }

@app.get("/balance")
def balance(request: Request, db: Session = Depends(get_db)):
    email = current_email(request)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # ดึงข้อมูล user และ balance จาก details table
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # ดึง balance จาก details table
    user_details = db.query(Details).filter(Details.user_id == user.id).first()
    if not user_details:
        # ถ้าไม่มี details record ให้สร้างใหม่
        user_details = Details(user_id=user.id, balance=Decimal('0.00'))
        db.add(user_details)
        db.commit()
        db.refresh(user_details)
    
    return {
        "amount": float(user_details.balance),
        "currency": "THB",
        "user_id": user.id,
        "last_updated": user_details.updated_at
    }

@app.get("/reports")
def reports(request: Request, db: Session = Depends(get_db)):
    must_admin(request)
    return {"items": [{"id": 1, "name": "Report A"}]}

@app.post("/api/register")
async def register(payload: RegisterPayload, db: Session = Depends(get_db)):
    # ตรวจสอบข้อมูลเหมือนโค้ดเก่า (age, phone, email, etc.)
    if payload.password != payload.confirm_password:
        return JSONResponse({"error": "Passwords do not match"}, status_code=400)
    if payload.age < 20:
        return JSONResponse({"error": "Age must be at least 20"}, status_code=400)
    if not re.fullmatch(r"0\d{9}", payload.phone):
        return JSONResponse({"error": "Invalid phone number"}, status_code=400)
    if not payload.email.endswith("@gmail.com"):
        return JSONResponse({"error": "Email must end with @gmail.com"}, status_code=400)

    email_norm = payload.email.lower()
    existed = db.query(User).filter(func.lower(User.email) == email_norm).first()
    if existed:
        return JSONResponse({"error": "Email already exists"}, status_code=400)
    
    # ตรวจสอบ phone ซ้ำ
    existed_phone = db.query(User).filter(User.phone == payload.phone).first()
    if existed_phone:
        return JSONResponse({"error": "Phone number already exists"}, status_code=400)

    user = User(
        full_name=payload.full_name,
        age=payload.age,
        phone=payload.phone,
        email=email_norm,
        password_hash=User.bcrypt.hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # สร้าง Details (Balance) สำหรับ User ใหม่ด้วยยอดเงิน 0.00
    user_details = Details(
        user_id=user.id,
        balance=Decimal('0.00')
    )
    db.add(user_details)
    db.commit()
    
    return {"message": "Registered successfully"}

@app.post("/login")
async def login(payload: LoginPayload, db: Session = Depends(get_db)):
    email_norm = payload.email.lower()
    user = db.query(User).filter(func.lower(User.email) == email_norm).first()
    
    if not user:
        return JSONResponse({"error": "Invalid email or password"}, status_code=400)
    
    if not User.bcrypt.verify(payload.password, user.password_hash):
        return JSONResponse({"error": "Invalid email or password"}, status_code=400)

    # สำเร็จ - set cookie และส่ง response
    resp = JSONResponse({
        "message": "Login successful",
        "email": email_norm,
        "user": {
            "full_name": user.full_name,
            "email": user.email,
            "is_admin": email_norm == ADMIN_EMAIL
        }
    })
    resp.set_cookie(COOKIE_NAME, email_norm, max_age=7*24*60*60, path="/", httponly=True, samesite="Lax")
    return resp

@app.post("/api/logout")
async def logout():
    resp = JSONResponse({"message": "Logged out"})
    resp.delete_cookie(COOKIE_NAME, path="/")
    return resp

@app.post("/logout")
async def logout_simple():
    resp = JSONResponse({"message": "Logged out"})
    resp.delete_cookie(COOKIE_NAME, path="/")
    return resp

@app.post("/deposit")
async def deposit(payload: DepositPayload, request: Request, db: Session = Depends(get_db)):
    email = current_email(request)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")
    
    print(f"💰 Deposit request: {email} wants to deposit {payload.amount}")
    
    # ดึงข้อมูล user
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # อัพเดต balance
    user_details = db.query(Details).filter(Details.user_id == user.id).first()
    if not user_details:
        user_details = Details(user_id=user.id, balance=Decimal('0.00'))
        db.add(user_details)
    
    old_balance = float(user_details.balance)
    user_details.balance += Decimal(str(payload.amount))
    new_balance = float(user_details.balance)
    db.commit()
    
    print(f"✅ Deposit successful: {email} balance updated from {old_balance} to {new_balance}")
    
    return {
        "message": "Deposit successful", 
        "new_balance": new_balance,
        "deposited_amount": payload.amount
    }

@app.post("/withdraw")
async def withdraw(payload: WithdrawPayload, request: Request, db: Session = Depends(get_db)):
    email = current_email(request)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")
    
    print(f"💸 Withdraw request: {email} wants to withdraw {payload.amount}")
    
    # ดึงข้อมูล user
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # ตรวจสอบ balance เพียงพอ
    user_details = db.query(Details).filter(Details.user_id == user.id).first()
    if not user_details or user_details.balance < Decimal(str(payload.amount)):
        print(f"❌ Insufficient balance: {email} has {user_details.balance if user_details else 0}, wants {payload.amount}")
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # หัก balance
    old_balance = float(user_details.balance)
    user_details.balance -= Decimal(str(payload.amount))
    new_balance = float(user_details.balance)
    db.commit()
    
    print(f"✅ Withdrawal successful: {email} balance updated from {old_balance} to {new_balance}")
    
    return {
        "message": "Withdrawal successful", 
        "new_balance": new_balance,
        "withdrawn_amount": payload.amount
    }
