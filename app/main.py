# app/main.py
import re
from fastapi import FastAPI, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from app.models import SessionLocal, User, create_db


# ---- เพิ่ม import เหล่านี้ด้านบน ----
import os
from fastapi.responses import JSONResponse
from starlette import status  # ถ้ายังไม่มีบรรทัดนี้

# ---- ตั้งค่าบัญชีแอดมิน (อ่านจาก .env ถ้ามี) ----
load_dotenv()
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "H2W@admin.com")


# Static & templates
app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# ---------- Startup: make sure tables exist ----------
@app.on_event("startup")
def on_startup():
    create_db()


# ---------- PAGES ----------
@app.get("/")
async def root():
    return RedirectResponse(url="/login")
@app.get("/", response_class=HTMLResponse)
async def get_register_page(request: Request):
    # เสิร์ฟหน้า register พร้อม context ว่างสำหรับ error/old
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "error": None, "old": {}},
    )


@app.get("/register", response_class=HTMLResponse)
async def get_register_alias(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "error": None, "old": {}},
    )


@app.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    if request.cookies.get("userEmail") != ADMIN_EMAIL:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/reports", response_class=HTMLResponse)
async def get_reports(request: Request):
    if request.cookies.get("userEmail") != ADMIN_EMAIL:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("reports.html", {"request": request})

@app.get("/balance", response_class=HTMLResponse)
async def balance_page(request: Request):
    # บังคับให้ต้อง login ก่อน (มีคุกกี้ useremail)
    if not request.cookies.get("useremail"):
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse("balance.html", {"request": request})


# ---------- APIS ----------
@app.post("/api/register", response_class=HTMLResponse)
async def post_register(request: Request):
    # -------- อ่านค่าจากฟอร์ม --------
    form = await request.form()
    full_name = (form.get("full_name") or "").strip()
    age_raw   = (form.get("age") or "").strip()
    phone     = (form.get("phone") or "").strip()
    email     = (form.get("email") or "").strip()
    password  = (form.get("password") or "").strip()
    confirm   = (form.get("confirm_password") or "").strip()

    # เก็บค่าเดิมเพื่อส่งกลับไปเติมในช่อง input เมื่อมี error
    old = {
        "full_name": full_name,
        "age": age_raw,
        "phone": phone,
        "email": email,
    }

    # -------- ตรวจเงื่อนไข --------
    # 1) รหัสผ่านตรงกัน
    if password != confirm:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Passwords do not match.", "old": old},
            status_code=400,
        )

    # 2) อายุต้องเป็นตัวเลขและ >= 20
    try:
        age = int(age_raw)
    except ValueError:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Age must be a number.", "old": old},
            status_code=400,
        )
    if age < 20:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Age must be at least 20.", "old": old},
            status_code=400,
        )

    # 3) เบอร์โทรต้องขึ้นต้น 0 และยาว 10 หลัก
    if not re.fullmatch(r"0\d{9}", phone):
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Phone number must start with 0 and be exactly 10 digits.",
                "old": old,
            },
            status_code=400,
        )

    # 4) อีเมลต้องลงท้ายด้วย @gmail.com และมี local-part ก่อน @ อย่างน้อย 1 ตัว
    email_l = email.lower()
    if not email_l.endswith("@gmail.com") or email_l.rsplit("@", 1)[0] == "":
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Email must end with @gmail.com.", "old": old},
            status_code=400,
        )

    # 5) ตรวจซ้ำใน DB
    db: Session = SessionLocal()
    try:
        dup = db.query(User).filter(User.email == email_l).first()
        if dup:
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": "Email already exists.", "old": old},
                status_code=400,
            )

        # -------- บันทึกถ้าผ่านทุกเงื่อนไข --------
        user = User(
            full_name=full_name,
            age=age,
            phone=phone,
            email=email_l,
            password_hash=bcrypt.hash(password),
        )
        db.add(user)
        db.commit()
    finally:
        db.close()
    # สำเร็จ -> ไปหน้า login
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/login")
async def post_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email.strip()).first()

        if not user:
            # ไม่พบอีเมลในระบบ
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Account does not exist."},
                status_code=400
            )

        if not bcrypt.verify(password, user.password_hash):
            # รหัสผ่านไม่ถูก
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Invalid password."},
                status_code=400
            )

        # สำเร็จ → ตั้งคุกกี้ แล้วเด้งไป /balance
        resp = RedirectResponse(url="/balance", status_code=status.HTTP_303_SEE_OTHER)
        # เก็บอีเมลไว้ 7 วัน
        resp.set_cookie(key="useremail", value=user.email, max_age=7*24*60*60, path="/")
        return resp
    finally:
        db.close()

@app.post("/api/logout")
async def api_logout():
    resp = JSONResponse({"message": "Logged out"})
    resp.delete_cookie("userEmail", path="/")
    return resp

