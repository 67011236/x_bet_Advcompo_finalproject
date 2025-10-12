from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os, re
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal

# import ของคุณเอง
from .models import SessionLocal, User, Credit, Report, Game1, Game2, Game2Stats, create_db, ensure_admin

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

class ReportPayload(BaseModel):
    title: str
    category: str
    description: str

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
    
    # ดึงข้อมูล user และ balance จาก credit table
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # ดึง balance จาก credit table
    user_credit = db.query(Credit).filter(Credit.user_id == user.id).first()
    if not user_credit:
        # ถ้าไม่มี credit record ให้สร้างใหม่
        user_credit = Credit(user_id=user.id, balance=Decimal('0.00'))
        db.add(user_credit)
        db.commit()
        db.refresh(user_credit)
    
    return {
        "amount": float(user_credit.balance),
        "currency": "THB",
        "user_id": user.id,
        "last_updated": user_credit.updated_at
    }

@app.get("/reports")
def reports(request: Request, db: Session = Depends(get_db)):
    must_admin(request)
    
    # ดึง reports ทั้งหมดพร้อมข้อมูล user
    reports = db.query(Report).join(User).order_by(Report.created_at.desc()).all()
    
    reports_data = []
    for report in reports:
        reports_data.append({
            "id": report.id,
            "title": report.title,
            "category": report.category,
            "description": report.description,
            "status": report.status,
            "user_email": report.user.email,
            "user_name": report.user.full_name,
            "created_at": report.created_at.isoformat(),
            "updated_at": report.updated_at.isoformat()
        })
    
    return {"reports": reports_data}

@app.post("/api/submit-report")
async def submit_report(payload: ReportPayload, request: Request, db: Session = Depends(get_db)):
    email = current_email(request)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # ตรวจสอบข้อมูล
    if not payload.title or not payload.category or not payload.description:
        raise HTTPException(status_code=400, detail="All fields are required")
    
    if payload.category not in ["technical", "payment", "account", "betting", "suggestion", "other"]:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    # หา user
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"📝 Report submission: {email} - {payload.title[:50]}...")
    
    # สร้าง report ใหม่
    new_report = Report(
        user_id=user.id,
        title=payload.title.strip(),
        category=payload.category,
        description=payload.description.strip(),
        status="pending"
    )
    
    try:
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
        
        print(f"✅ Report saved successfully: ID {new_report.id}")
        
        return {
            "message": "Report submitted successfully",
            "report_id": new_report.id,
            "status": "pending"
        }
        
    except Exception as e:
        print(f"❌ Error saving report: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save report")

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
    
    # สร้าง Credit (Balance) สำหรับ User ใหม่ด้วยยอดเงิน 0.00
    user_credit = Credit(
        user_id=user.id,
        balance=Decimal('0.00')
    )
    db.add(user_credit)
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
    user_credit = db.query(Credit).filter(Credit.user_id == user.id).first()
    if not user_credit:
        user_credit = Credit(user_id=user.id, balance=Decimal('0.00'))
        db.add(user_credit)
    
    old_balance = float(user_credit.balance)
    user_credit.balance += Decimal(str(payload.amount))
    new_balance = float(user_credit.balance)
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
    user_credit = db.query(Credit).filter(Credit.user_id == user.id).first()
    if not user_credit or user_credit.balance < Decimal(str(payload.amount)):
        print(f"❌ Insufficient balance: {email} has {user_credit.balance if user_credit else 0}, wants {payload.amount}")
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # หัก balance
    old_balance = float(user_credit.balance)
    user_credit.balance -= Decimal(str(payload.amount))
    new_balance = float(user_credit.balance)
    db.commit()
    
    print(f"✅ Withdrawal successful: {email} balance updated from {old_balance} to {new_balance}")
    
    return {
        "message": "Withdrawal successful", 
        "new_balance": new_balance,
        "withdrawn_amount": payload.amount
    }

# ===============================
# Game Betting APIs
# ===============================
class GameBetPayload(BaseModel):
    game_type: str  # "wheel" or "rps" (rock-paper-scissors)
    bet_amount: float
    player_choice: str = None  # For RPS: "rock", "paper", "scissors"
    
class GameResultPayload(BaseModel):
    game_type: str
    result: str  # "win", "lose", "tie"
    bet_amount: float
    win_amount: float

class Game1PlayPayload(BaseModel):
    bet_amount: int
    selected_color: str  # "blue" or "white"
    result_color: str   # "blue" or "white"
    won: bool
    payout_amount: int

@app.post("/api/place-bet")
async def place_bet(payload: GameBetPayload, request: Request, db: Session = Depends(get_db)):
    """
    Place a bet for any game
    """
    email = current_email(request)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if payload.bet_amount <= 0:
        raise HTTPException(status_code=400, detail="Bet amount must be greater than 0")
    
    # Validate game type
    if payload.game_type not in ["wheel", "rps"]:
        raise HTTPException(status_code=400, detail="Invalid game type")
    
    # For RPS, validate player choice
    if payload.game_type == "rps" and payload.player_choice not in ["rock", "paper", "scissors"]:
        raise HTTPException(status_code=400, detail="Invalid player choice for Rock Paper Scissors")
    
    print(f"🎮 Game bet placed: {email} - {payload.game_type} - {payload.bet_amount} THB")
    
    # Check user balance
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_credit = db.query(Credit).filter(Credit.user_id == user.id).first()
    if not user_credit or user_credit.balance < Decimal(str(payload.bet_amount)):
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    return {
        "message": "Bet placed successfully",
        "game_type": payload.game_type,
        "bet_amount": payload.bet_amount,
        "player_choice": payload.player_choice,
        "current_balance": float(user_credit.balance)
    }

@app.post("/api/game-result")
async def process_game_result(payload: GameResultPayload, request: Request, db: Session = Depends(get_db)):
    """
    Process game result and update user balance
    """
    email = current_email(request)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if payload.result not in ["win", "lose", "tie"]:
        raise HTTPException(status_code=400, detail="Invalid game result")
    
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_credit = db.query(Credit).filter(Credit.user_id == user.id).first()
    if not user_credit:
        raise HTTPException(status_code=404, detail="User credit not found")
    
    old_balance = float(user_credit.balance)
    
    # Update balance based on result
    if payload.result == "win":
        # Player wins - add winnings minus the bet (net profit)
        net_profit = payload.win_amount - payload.bet_amount
        user_credit.balance += Decimal(str(net_profit))
    elif payload.result == "lose":
        # Player loses - subtract bet amount
        user_credit.balance -= Decimal(str(payload.bet_amount))
    # For tie, balance remains the same
    
    new_balance = float(user_credit.balance)
    db.commit()
    
    print(f"🎮 Game result processed: {email} - {payload.result} - Balance: {old_balance} -> {new_balance}")
    
    return {
        "message": "Game result processed",
        "result": payload.result,
        "old_balance": old_balance,
        "new_balance": new_balance,
        "balance_change": new_balance - old_balance
    }

# ===============================
# Dashboard Statistics API
# ===============================
@app.get("/api/dashboard-stats")
async def get_dashboard_stats(request: Request, db: Session = Depends(get_db)):
    """
    Get dashboard statistics: total users and total reports
    """
    must_admin(request)  # Only admin can access dashboard stats
    
    try:
        # Count total users
        total_users = db.query(User).count()
        
        # Count total reports
        total_reports = db.query(Report).count()
        
        return {
            "total_users": total_users,
            "total_reports": total_reports,
            "status": "success"
        }
    except Exception as e:
        print(f"❌ Error fetching dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/game-stats")
async def get_game_stats(request: Request, db: Session = Depends(get_db)):
    """
    Get game statistics for pie chart: Game1 (Premium Wheel) vs Game2 (Rock Paper Scissors)
    """
    try:
        must_admin(request)  # Only admin can access game stats
        print("📊 Admin accessing game stats API...")
    except Exception as e:
        print(f"❌ Authentication failed for game-stats: {e}")
        raise
    
    try:
        # Count total Game1 plays
        game1_total = db.query(Game1).count()
        
        # Count total Game2 plays  
        game2_total = db.query(Game2).count()
        
        # Calculate total plays
        total_plays = game1_total + game2_total
        
        # Calculate percentages
        if total_plays > 0:
            game1_percentage = round((game1_total / total_plays) * 100, 1)
            game2_percentage = round((game2_total / total_plays) * 100, 1)
        else:
            game1_percentage = 50.0
            game2_percentage = 50.0
        
        # Get recent activities (last 10 games from both tables)
        from sqlalchemy import text
        
        recent_activities_query = text("""
            SELECT 
                'game1' as game_type,
                u.email,
                g.win_loss_amount,
                CASE WHEN g.won = 1 THEN 'win' ELSE 'lose' END as result,
                g.played_at
            FROM game1 g
            JOIN users u ON g.user_id = u.id
            UNION ALL
            SELECT 
                'game2' as game_type,
                u.email,
                g.win_loss_amount,
                g.result,
                g.played_at
            FROM game2 g
            JOIN users u ON g.user_id = u.id
            ORDER BY played_at DESC
            LIMIT 10
        """)
        
        recent_results = db.execute(recent_activities_query).fetchall()
        
        activities = []
        for result in recent_results:
            # Calculate time ago
            from datetime import datetime, timedelta
            played_time = result[4]  # played_at
            time_diff = datetime.utcnow() - played_time
            
            if time_diff.days > 0:
                time_ago = f"{time_diff.days}d ago"
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                time_ago = f"{hours}h ago"
            elif time_diff.seconds > 60:
                minutes = time_diff.seconds // 60
                time_ago = f"{minutes}m ago"
            else:
                time_ago = "Just now"
            
            activities.append({
                "id": result[1],  # email
                "amount": f"{abs(float(result[2])):.2f} THB",
                "type": result[3],  # win/lose/tie
                "time": time_ago,
                "game": result[0]  # game1 or game2
            })
        
        return {
            "game_stats": [
                {
                    "name": "Premium Wheel",
                    "percentage": game1_percentage,
                    "color": "#71ddff",
                    "total_plays": game1_total
                },
                {
                    "name": "Rock-Paper-Scissors", 
                    "percentage": game2_percentage,
                    "color": "#4a9eff",
                    "total_plays": game2_total
                }
            ],
            "recent_activities": activities,
            "total_plays": total_plays,
            "status": "success"
        }
        
    except Exception as e:
        print(f"❌ Error fetching game stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/game1/count")
async def get_game1_count(db: Session = Depends(get_db)):
    """
    Get total count of Game1 plays (accessible to authenticated users)
    """
    try:
        count = db.query(Game1).count()
        return {"count": count, "game": "Premium Wheel"}
    except Exception as e:
        print(f"❌ Error getting Game1 count: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/game2/count")
async def get_game2_count(db: Session = Depends(get_db)):
    """
    Get total count of Game2 plays (accessible to authenticated users)
    """
    try:
        count = db.query(Game2).count()
        return {"count": count, "game": "Rock-Paper-Scissors"}
    except Exception as e:
        print(f"❌ Error getting Game2 count: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/report-categories")
async def get_report_categories(db: Session = Depends(get_db)):
    """
    Get report categories statistics from database (real-time data)
    """
    try:
        # Query to count reports by category
        category_stats = db.query(
            Report.category,
            func.count(Report.id).label('count')
        ).group_by(Report.category).all()
        
        # Create a mapping with all possible categories (with 0 if no reports)
        categories_map = {
            'technical': 0,
            'payment': 0,
            'account': 0,
            'betting': 0,
            'suggestion': 0,
            'other': 0
        }
        
        # Update with actual counts from database
        for category, count in category_stats:
            if category in categories_map:
                categories_map[category] = count
        
        # Format response for frontend
        report_categories = [
            {
                "type": "Technical Issue",
                "value": categories_map['technical'],
                "color": "#71ddff"
            },
            {
                "type": "Payment Issue", 
                "value": categories_map['payment'],
                "color": "#71ddff"
            },
            {
                "type": "Account Issue",
                "value": categories_map['account'],
                "color": "#71ddff"
            },
            {
                "type": "Betting Issue",
                "value": categories_map['betting'],
                "color": "#71ddff"
            },
            {
                "type": "Suggestion",
                "value": categories_map['suggestion'],
                "color": "#71ddff"
            },
            {
                "type": "Other",
                "value": categories_map['other'],
                "color": "#71ddff"
            }
        ]
        
        print(f"📊 Report categories stats: {categories_map}")
        return {"categories": report_categories, "total_reports": sum(categories_map.values())}
        
    except Exception as e:
        print(f"❌ Error getting report categories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ===============================
# Game1 Play Tracking API
# ===============================
@app.post("/api/game1-play")
async def record_game1_play(payload: Game1PlayPayload, request: Request, db: Session = Depends(get_db)):
    """
    Record a game1 play session in the database
    """
    email = current_email(request)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Validate input
    if payload.selected_color not in ["blue", "white"]:
        raise HTTPException(status_code=400, detail="Invalid selected color")
    
    if payload.result_color not in ["blue", "white"]:
        raise HTTPException(status_code=400, detail="Invalid result color")
    
    if payload.bet_amount <= 0:
        raise HTTPException(status_code=400, detail="Bet amount must be positive")
    
    try:
        # Create new game1 play record
        game1_play = Game1(
            user_id=email,  # ใช้ email เป็น user_id
            bet_amount=payload.bet_amount,
            selected_color=payload.selected_color,
            result_color=payload.result_color,
            won=1 if payload.won else 0,
            payout_amount=payload.payout_amount
        )
        
        db.add(game1_play)
        db.commit()
        
        print(f"🎮 Game1 play recorded: {email} - {payload.selected_color} vs {payload.result_color} - {'Won' if payload.won else 'Lost'} {payload.payout_amount}")
        
        return {
            "message": "Game1 play recorded successfully",
            "play_id": game1_play.id,
            "status": "success"
        }
        
    except Exception as e:
        print(f"❌ Error recording game1 play: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to record game play")

# ===============================
# Game1 Enhanced APIs (ใหม่)
# ===============================

class Game1BetPayload(BaseModel):
    bet_amount: float
    selected_color: str  # "blue" หรือ "white"
    result_color: str = None  # ผลลัพธ์จากล้อ Frontend (optional เผื่อใช้ fallback)

class Game1HistoryParams(BaseModel):
    limit: int = 20
    offset: int = 0

@app.post("/api/game1/play")
async def play_game1(payload: Game1BetPayload, request: Request, db: Session = Depends(get_db)):
    """
    เล่น Game1 - วงล้อสี (API ใหม่ที่สมบูรณ์)
    """
    email = current_email(request)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # หา user จาก email
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate input
    if payload.selected_color not in ["blue", "white"]:
        raise HTTPException(status_code=400, detail="Selected color must be 'blue' or 'white'")
    
    if payload.bet_amount <= 0:
        raise HTTPException(status_code=400, detail="Bet amount must be positive")
    
    try:
        # ตรวจสอบยอดเงิน
        credit = db.query(Credit).filter(Credit.user_id == user.id).first()
        if not credit or float(credit.balance) < payload.bet_amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        current_balance = float(credit.balance)
        
        # ใช้ผลลัพธ์จาก Frontend หรือสุ่มใหม่ถ้าไม่ได้ส่งมา
        if payload.result_color and payload.result_color in ['blue', 'white']:
            result_color = payload.result_color
        else:
            # Fallback: สุ่มผลลัพธ์ (50% โอกาสแต่ละสี)
            import random
            result_color = random.choice(['blue', 'white'])
        
        won = 1 if payload.selected_color == result_color else 0
        
        # คำนวณจำนวนเงินที่ชนะ/แพ้
        if won:
            win_loss_amount = payload.bet_amount  # ชนะได้เท่าที่เดิมพัน
            new_balance = current_balance + payload.bet_amount
        else:
            win_loss_amount = -payload.bet_amount  # แพ้เสียเท่าที่เดิมพัน
            new_balance = current_balance - payload.bet_amount
        
        # อัพเดทยอดเงินในตาราง credit
        credit.balance = Decimal(str(new_balance))
        credit.updated_at = func.now()  # อัพเดทเวลา
        
        # บันทึกผลการเล่น
        game1_play = Game1(
            user_id=user.id,  # ใช้ user.id แทน email
            bet_amount=Decimal(str(payload.bet_amount)),
            selected_color=payload.selected_color,
            result_color=result_color,
            won=won,
            win_loss_amount=Decimal(str(win_loss_amount)),
            balance_before=Decimal(str(current_balance)),
            balance_after=Decimal(str(new_balance))
        )
        
        # เพิ่มทั้ง credit และ game1_play ในครั้งเดียว
        db.add(credit)  # อัพเดท credit balance
        db.add(game1_play)  # เพิ่มการเล่นใหม่
        db.commit()  # commit ทั้งสองอย่างพร้อมกัน
        db.refresh(game1_play)
        db.refresh(credit)  # refresh credit เพื่อให้แน่ใจว่าอัพเดทแล้ว
        
        print(f"🎮 Game1 played: {email} bet {payload.bet_amount} on {payload.selected_color}, result: {result_color}, {'WON' if won else 'LOST'}")
        print(f"💰 Balance updated in DB: {current_balance} → {float(credit.balance)} (user_id: {user.id})")
        print(f"📊 Game recorded in DB with ID: {game1_play.id}")
        
        return {
            "success": True,
            "result": {
                "game_id": game1_play.id,
                "selected_color": payload.selected_color,
                "result_color": result_color,
                "won": bool(won),
                "bet_amount": payload.bet_amount,
                "win_loss_amount": float(win_loss_amount),
                "balance_before": current_balance,
                "balance_after": new_balance,
                "message": "" if won else ""
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in game1 play: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to process game")

@app.get("/api/game1/history")
async def get_game1_history(request: Request, limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    """
    ดึงประวัติการเล่น Game1 ของผู้ใช้
    """
    email = current_email(request)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # หา user จาก email
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # ดึงประวัติการเล่น
        games = db.query(Game1).filter(Game1.user_id == user.id)\
                              .order_by(Game1.played_at.desc())\
                              .offset(offset)\
                              .limit(limit)\
                              .all()
        
        history = []
        for game in games:
            history.append({
                "id": game.id,
                "bet_amount": float(game.bet_amount),
                "selected_color": game.selected_color,
                "result_color": game.result_color,
                "won": bool(game.won),
                "win_loss_amount": float(game.win_loss_amount),
                "balance_before": float(game.balance_before),
                "balance_after": float(game.balance_after),
                "played_at": game.played_at.isoformat()
            })
        
        return {
            "success": True,
            "history": history,
            "total_records": len(history)
        }
        
    except Exception as e:
        print(f"❌ Error fetching game1 history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")

@app.get("/api/game1/stats")
async def get_game1_stats(request: Request, db: Session = Depends(get_db)):
    """
    ดึงสถิติการเล่น Game1 ของผู้ใช้
    """
    email = current_email(request)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # หา user จาก email
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # ใช้ raw SQL เพื่อคำนวณสถิติ
        from sqlalchemy import text
        
        stats_query = text("""
            SELECT 
                COUNT(*) as total_games,
                COUNT(CASE WHEN won = 1 THEN 1 END) as total_wins,
                COUNT(CASE WHEN won = 0 THEN 1 END) as total_losses,
                COALESCE(SUM(bet_amount), 0) as total_bet_amount,
                COALESCE(SUM(CASE WHEN won = 1 THEN win_loss_amount ELSE 0 END), 0) as total_win_amount,
                COALESCE(SUM(CASE WHEN won = 0 THEN ABS(win_loss_amount) ELSE 0 END), 0) as total_loss_amount,
                COALESCE(SUM(win_loss_amount), 0) as net_profit_loss,
                MIN(played_at) as first_played_at,
                MAX(played_at) as last_played_at
            FROM game1 
            WHERE user_id = :user_id
        """)
        
        result = db.execute(stats_query, {"user_id": user.id}).fetchone()
        
        if not result or result[0] == 0:
            # ยังไม่เคยเล่น
            return {
                "success": True,
                "stats": {
                    "total_games": 0,
                    "total_wins": 0,
                    "total_losses": 0,
                    "total_bet_amount": 0.0,
                    "total_win_amount": 0.0,
                    "total_loss_amount": 0.0,
                    "net_profit_loss": 0.0,
                    "win_percentage": 0.0,
                    "first_played_at": None,
                    "last_played_at": None
                }
            }
        
        total_games = result[0]
        total_wins = result[1]
        win_percentage = (total_wins / total_games * 100) if total_games > 0 else 0
        
        return {
            "success": True,
            "stats": {
                "total_games": total_games,
                "total_wins": total_wins,
                "total_losses": result[2],
                "total_bet_amount": float(result[3]),
                "total_win_amount": float(result[4]),
                "total_loss_amount": float(result[5]),
                "net_profit_loss": float(result[6]),
                "win_percentage": round(win_percentage, 2),
                "first_played_at": result[7].isoformat() if result[7] else None,
                "last_played_at": result[8].isoformat() if result[8] else None
            }
        }
        
    except Exception as e:
        print(f"❌ Error fetching game1 stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stats")

# Admin API สำหรับดูสถิติทุกคน
@app.get("/api/admin/game1/all-stats")
async def get_all_users_game1_stats(request: Request, db: Session = Depends(get_db)):
    """
    ดึงสถิติการเล่น Game1 ของผู้ใช้ทุกคน (Admin เท่านั้น)
    """
    must_admin(request)
    
    try:
        from sqlalchemy import text
        
        all_stats_query = text("""
            SELECT 
                u.id,
                u.full_name,
                u.email,
                COUNT(g.id) as total_games,
                COUNT(CASE WHEN g.won = 1 THEN 1 END) as total_wins,
                COALESCE(SUM(g.bet_amount), 0) as total_bet_amount,
                COALESCE(SUM(g.win_loss_amount), 0) as net_profit_loss,
                MAX(g.played_at) as last_played_at
            FROM users u
            LEFT JOIN game1 g ON u.id = g.user_id
            WHERE u.role = 'user'
            GROUP BY u.id, u.full_name, u.email
            HAVING COUNT(g.id) > 0
            ORDER BY total_games DESC, net_profit_loss DESC
            LIMIT 100
        """)
        
        results = db.execute(all_stats_query).fetchall()
        
        all_stats = []
        for result in results:
            total_games = result[3]
            total_wins = result[4]
            win_percentage = (total_wins / total_games * 100) if total_games > 0 else 0
            
            all_stats.append({
                "user_id": result[0],
                "full_name": result[1],
                "email": result[2],
                "total_games": total_games,
                "total_wins": total_wins,
                "total_losses": total_games - total_wins,
                "total_bet_amount": float(result[5]),
                "net_profit_loss": float(result[6]),
                "win_percentage": round(win_percentage, 2),
                "last_played_at": result[7].isoformat() if result[7] else None
            })
        
        return {
            "success": True,
            "all_stats": all_stats,
            "total_users": len(all_stats)
        }
        
    except Exception as e:
        print(f"❌ Error fetching all users game1 stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch all stats")

# ===============================
# Game2 (Rock Paper Scissors) APIs
# ===============================

class Game2BetPayload(BaseModel):
    bet_amount: float
    player_choice: str  # "rock", "paper", "scissors"
    bot_choice: str     # "rock", "paper", "scissors" 
    result: str         # "win", "lose", "tie"

@app.post("/api/game2/play")
async def play_game2(payload: Game2BetPayload, request: Request, db: Session = Depends(get_db)):
    """
    เล่น Game2 - Rock Paper Scissors
    """
    email = current_email(request)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # หา user จาก email
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate input
    valid_choices = ["rock", "paper", "scissors"]
    if payload.player_choice not in valid_choices:
        raise HTTPException(status_code=400, detail="Player choice must be 'rock', 'paper', or 'scissors'")
    
    if payload.bot_choice not in valid_choices:
        raise HTTPException(status_code=400, detail="Bot choice must be 'rock', 'paper', or 'scissors'")
    
    if payload.result not in ["win", "lose", "tie"]:
        raise HTTPException(status_code=400, detail="Result must be 'win', 'lose', or 'tie'")
    
    if payload.bet_amount <= 0:
        raise HTTPException(status_code=400, detail="Bet amount must be positive")
    
    try:
        # ตรวจสอบยอดเงิน
        credit = db.query(Credit).filter(Credit.user_id == user.id).first()
        if not credit or float(credit.balance) < payload.bet_amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        current_balance = float(credit.balance)
        
        # คำนวณจำนวนเงินที่ชนะ/แพ้
        if payload.result == "win":
            win_loss_amount = payload.bet_amount * 2  # ชนะได้ 2 เท่า
            new_balance = current_balance + payload.bet_amount
        elif payload.result == "lose":
            win_loss_amount = -payload.bet_amount  # แพ้เสียเท่าที่เดิมพัน
            new_balance = current_balance - payload.bet_amount
        else:  # tie
            win_loss_amount = 0  # เสมอไม่ได้ไม่เสีย
            new_balance = current_balance
        
        # อัพเดทยอดเงินในตาราง credit
        credit.balance = Decimal(str(new_balance))
        credit.updated_at = func.now()
        
        # บันทึกผลการเล่น
        game2_play = Game2(
            user_id=user.id,
            bet_amount=Decimal(str(payload.bet_amount)),
            player_choice=payload.player_choice,
            bot_choice=payload.bot_choice,
            result=payload.result,
            win_loss_amount=Decimal(str(win_loss_amount)),
            balance_before=Decimal(str(current_balance)),
            balance_after=Decimal(str(new_balance))
        )
        
        # อัพเดทสถิติ Game2 
        stats = db.query(Game2Stats).filter(Game2Stats.user_id == user.id).first()
        if not stats:
            # สร้างสถิติใหม่ถ้ายังไม่มี
            stats = Game2Stats(
                user_id=user.id,
                total_games_played=0,
                total_wins=0,
                total_losses=0,
                total_ties=0,
                total_bet_amount=Decimal('0.00'),
                total_win_amount=Decimal('0.00'),
                total_loss_amount=Decimal('0.00'),
                net_profit_loss=Decimal('0.00'),
                rock_played=0,
                paper_played=0,
                scissors_played=0,
                first_played_at=func.now()
            )
            db.add(stats)
        
        # อัพเดทสถิติ
        stats.total_games_played += 1
        stats.total_bet_amount += Decimal(str(payload.bet_amount))
        stats.last_played_at = func.now()
        
        if payload.result == "win":
            stats.total_wins += 1
            stats.total_win_amount += Decimal(str(payload.bet_amount))
        elif payload.result == "lose":
            stats.total_losses += 1
            stats.total_loss_amount += Decimal(str(payload.bet_amount))
        else:
            stats.total_ties += 1
        
        # นับตัวเลือก
        if payload.player_choice == "rock":
            stats.rock_played += 1
        elif payload.player_choice == "paper":
            stats.paper_played += 1
        elif payload.player_choice == "scissors":
            stats.scissors_played += 1
        
        stats.net_profit_loss = stats.total_win_amount - stats.total_loss_amount
        
        # บันทึกทั้งหมด
        db.add(credit)
        db.add(game2_play)
        db.add(stats)
        db.commit()
        db.refresh(game2_play)
        db.refresh(credit)
        db.refresh(stats)
        
        print(f"🎮 Game2 played: {email} bet {payload.bet_amount} - {payload.player_choice} vs {payload.bot_choice} = {payload.result}")
        print(f"💰 Balance updated: {current_balance} → {float(credit.balance)}")
        
        return {
            "success": True,
            "result": {
                "game_id": game2_play.id,
                "player_choice": payload.player_choice,
                "bot_choice": payload.bot_choice,
                "result": payload.result,
                "bet_amount": payload.bet_amount,
                "win_loss_amount": float(win_loss_amount),
                "balance_before": current_balance,
                "balance_after": new_balance,
                "message": f"You {payload.result}!"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in game2 play: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to process game")

@app.get("/api/game2/history")
async def get_game2_history(request: Request, limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    """
    ดึงประวัติการเล่น Game2 ของผู้ใช้
    """
    email = current_email(request)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        games = db.query(Game2).filter(Game2.user_id == user.id)\
                              .order_by(Game2.played_at.desc())\
                              .offset(offset)\
                              .limit(limit)\
                              .all()
        
        history = []
        for game in games:
            history.append({
                "id": game.id,
                "bet_amount": float(game.bet_amount),
                "player_choice": game.player_choice,
                "bot_choice": game.bot_choice,
                "result": game.result,
                "win_loss_amount": float(game.win_loss_amount),
                "balance_before": float(game.balance_before),
                "balance_after": float(game.balance_after),
                "played_at": game.played_at.isoformat()
            })
        
        return {
            "success": True,
            "history": history,
            "total_records": len(history)
        }
        
    except Exception as e:
        print(f"❌ Error fetching game2 history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")

@app.get("/api/game2/stats")
async def get_game2_stats(request: Request, db: Session = Depends(get_db)):
    """
    ดึงสถิติการเล่น Game2 ของผู้ใช้
    """
    email = current_email(request)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        stats = db.query(Game2Stats).filter(Game2Stats.user_id == user.id).first()
        
        if not stats:
            return {
                "success": True,
                "stats": {
                    "total_games": 0,
                    "total_wins": 0,
                    "total_losses": 0,
                    "total_ties": 0,
                    "total_bet_amount": 0.0,
                    "total_win_amount": 0.0,
                    "total_loss_amount": 0.0,
                    "net_profit_loss": 0.0,
                    "win_percentage": 0.0,
                    "rock_played": 0,
                    "paper_played": 0,
                    "scissors_played": 0,
                    "first_played_at": None,
                    "last_played_at": None
                }
            }
        
        total_games = stats.total_games_played
        win_percentage = (stats.total_wins / total_games * 100) if total_games > 0 else 0
        
        return {
            "success": True,
            "stats": {
                "total_games": total_games,
                "total_wins": stats.total_wins,
                "total_losses": stats.total_losses,
                "total_ties": stats.total_ties,
                "total_bet_amount": float(stats.total_bet_amount),
                "total_win_amount": float(stats.total_win_amount),
                "total_loss_amount": float(stats.total_loss_amount),
                "net_profit_loss": float(stats.net_profit_loss),
                "win_percentage": round(win_percentage, 2),
                "rock_played": stats.rock_played,
                "paper_played": stats.paper_played,
                "scissors_played": stats.scissors_played,
                "first_played_at": stats.first_played_at.isoformat() if stats.first_played_at else None,
                "last_played_at": stats.last_played_at.isoformat() if stats.last_played_at else None
            }
        }
        
    except Exception as e:
        print(f"❌ Error fetching game2 stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stats")
