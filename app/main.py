from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models import SessionLocal, User, create_db, RegisterIn, RegisterOut, hash_password

app = FastAPI()

# เสิร์ฟไฟล์ static + templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# สร้างตารางครั้งแรก
create_db()

@app.get("/", response_class=HTMLResponse)
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/api/register", response_model=RegisterOut)
async def api_register(payload: RegisterIn):
    # validate ด้วย Pydantic แล้ว จากนั้นบันทึก DB
    db = SessionLocal()
    try:
        # กัน email ซ้ำ
        if db.query(User).filter(User.email == str(payload.email)).first():
            raise HTTPException(status_code=400, detail="Email already exists")

        user = User(
            full_name=payload.full_name,
            age=payload.age,
            phone=payload.phone,
            email=str(payload.email),
            password_hash=hash_password(payload.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return RegisterOut(id=user.id, email=user.email, full_name=user.full_name)
    finally:
        db.close()
