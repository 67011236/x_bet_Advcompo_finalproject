from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os, re
from sqlalchemy.orm import Session
from sqlalchemy import func

# import ของคุณเอง
from .models import SessionLocal, User, create_db, ensure_admin

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

# ---------- Endpoints ----------
@app.get("/")
def root(request: Request):
    return {"ok": True, "service": "fastapi", "email": current_email(request)}

@app.get("/me")
def me(request: Request):
    email = current_email(request)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"email": email, "is_admin": email == ADMIN_EMAIL}

@app.get("/balance")
def balance(request: Request, db: Session = Depends(get_db)):
    must_login(request)
    return {"amount": 12345}   # TODO: ดึงจาก DB จริง

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

    user = User(
        full_name=payload.full_name,
        age=payload.age,
        phone=payload.phone,
        email=email_norm,
        password_hash=User.bcrypt.hash(payload.password),
    )
    db.add(user)
    db.commit()
    return {"message": "Registered successfully"}

@app.post("/login")
async def login(payload: LoginPayload, db: Session = Depends(get_db)):
    email_norm = payload.email.lower()
    user = db.query(User).filter(func.lower(User.email) == email_norm).first()
    if not user:
        return JSONResponse({"error": "Account does not exist"}, status_code=400)
    if not User.bcrypt.verify(payload.password, user.password_hash):
        return JSONResponse({"error": "Invalid password"}, status_code=400)

    resp = JSONResponse({"message": "Logged in", "email": email_norm})
    resp.set_cookie(COOKIE_NAME, email_norm, max_age=7*24*60*60, path="/", httponly=True, samesite="Lax")
    return resp

@app.post("/api/logout")
async def logout():
    resp = JSONResponse({"message": "Logged out"})
    resp.delete_cookie(COOKIE_NAME, path="/")
    return resp
