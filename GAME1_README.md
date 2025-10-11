# Game1 Database Setup และ API Documentation

## ภาพรวม
ระบบ Game1 เป็นเกม "วงล้อสี" ที่ผู้เล่นเดิมพันเลือกสี (น้ำเงิน หรือ ขาว) และระบบจะสุ่มผลลัพธ์

## โครงสร้างฐานข้อมูล

### ตาราง `game1`
เก็บข้อมูลการเล่นแต่ละครั้ง

```sql
CREATE TABLE game1 (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    bet_amount NUMERIC(10, 2) NOT NULL,
    selected_color VARCHAR(10) NOT NULL,  -- 'blue' หรือ 'white'
    result_color VARCHAR(10) NOT NULL,    -- ผลลัพธ์จากระบบ
    won INTEGER NOT NULL,                 -- 1 = ชนะ, 0 = แพ้
    win_loss_amount NUMERIC(10, 2) NOT NULL,  -- +100 ถ้าชนะ, -100 ถ้าแพ้
    balance_before NUMERIC(10, 2) NOT NULL,   -- ยอดเงินก่อนเล่น
    balance_after NUMERIC(10, 2) NOT NULL,    -- ยอดเงินหลังเล่น
    played_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### ตาราง `game1_stats`
เก็บสถิติการเล่นของแต่ละผู้ใช้ (อัพเดทอัตโนมัติผ่าน Trigger)

```sql
CREATE TABLE game1_stats (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id),
    total_games_played INTEGER NOT NULL DEFAULT 0,
    total_wins INTEGER NOT NULL DEFAULT 0,
    total_losses INTEGER NOT NULL DEFAULT 0,
    total_bet_amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    total_win_amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    total_loss_amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    net_profit_loss NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    win_percentage NUMERIC(5, 2) DEFAULT 0.00,
    first_played_at TIMESTAMP NULL,
    last_played_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

## การติดตั้งฐานข้อมูล

### 1. การตั้งค่า Environment Variables
```bash
# PostgreSQL Connection
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=xbet_db
export DB_USER=postgres
export DB_PASSWORD=your_password
```

### 2. รันการติดตั้ง
```bash
# วิธีที่ 1: ใช้ Python Script
cd x_bet_Advcompo_finalproject
python setup_game1_database.py

# วิธีที่ 2: รัน SQL โดยตรงใน DBeaver หรือ psql
psql -h localhost -U postgres -d xbet_db -f create_game1_tables.sql
```

### 3. ติดตั้ง Python packages
```bash
pip install psycopg2-binary sqlalchemy fastapi
```

## API Endpoints

### 1. เล่นเกม
**POST** `/api/game1/play`

**Request Body:**
```json
{
  "bet_amount": 100.0,
  "selected_color": "blue"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "game_id": 123,
    "selected_color": "blue",
    "result_color": "blue",
    "won": true,
    "bet_amount": 100.0,
    "win_loss_amount": 100.0,
    "balance_before": 1000.0,
    "balance_after": 1100.0,
    "message": "ชนะแล้ว! 🎉"
  }
}
```

### 2. ดูประวัติการเล่น
**GET** `/api/game1/history?limit=20&offset=0`

**Response:**
```json
{
  "success": true,
  "history": [
    {
      "id": 123,
      "bet_amount": 100.0,
      "selected_color": "blue",
      "result_color": "blue",
      "won": true,
      "win_loss_amount": 100.0,
      "balance_before": 1000.0,
      "balance_after": 1100.0,
      "played_at": "2025-10-11T10:30:00"
    }
  ],
  "total_records": 1
}
```

### 3. ดูสถิติการเล่น
**GET** `/api/game1/stats`

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_games": 10,
    "total_wins": 6,
    "total_losses": 4,
    "total_bet_amount": 1000.0,
    "total_win_amount": 600.0,
    "total_loss_amount": 400.0,
    "net_profit_loss": 200.0,
    "win_percentage": 60.0,
    "first_played_at": "2025-10-10T14:20:00",
    "last_played_at": "2025-10-11T10:30:00"
  }
}
```

### 4. ดูสถิติทุกคน (Admin)
**GET** `/api/admin/game1/all-stats`

**Response:**
```json
{
  "success": true,
  "all_stats": [
    {
      "user_id": 1,
      "full_name": "John Doe",
      "email": "john@example.com",
      "total_games": 50,
      "total_wins": 25,
      "total_losses": 25,
      "total_bet_amount": 5000.0,
      "net_profit_loss": -200.0,
      "win_percentage": 50.0,
      "last_played_at": "2025-10-11T10:30:00"
    }
  ],
  "total_users": 1
}
```

## การใช้งาน Game1Service Class

```python
from game1_service import Game1Service

# เล่นเกม
with Game1Service() as game_service:
    result = game_service.play_game(
        user_id=1, 
        bet_amount=100.0, 
        selected_color="blue"
    )
    print(result)

# ดูสถิติ
with Game1Service() as game_service:
    stats = game_service.get_user_game_stats(user_id=1)
    print(stats)

# ดูประวัติ
with Game1Service() as game_service:
    history = game_service.get_user_game_history(user_id=1, limit=10)
    print(history)
```

## Features ของระบบ

### 🔄 Auto-Update สถิติ
- เมื่อมีการเล่นเกมใหม่ ระบบจะอัพเดทสถิติใน `game1_stats` อัตโนมัติผ่าน PostgreSQL Trigger

### 💰 การจัดการยอดเงิน
- ตรวจสอบยอดเงินก่อนเดิมพัน
- อัพเดทยอดเงินในตาราง `credit` ทันที
- บันทึกยอดเงินก่อนและหลังการเล่น

### 📊 สถิติแบบเรียลไทม์
- จำนวนครั้งที่เล่น, ชนะ, แพ้
- ยอดเดิมพันรวม, กำไร/ขาดทุนสุทธิ
- เปอร์เซ็นต์การชนะ
- วันที่เล่นครั้งแรกและล่าสุด

### 🎲 ระบบสุ่มที่ยุติธรรม
- ใช้ Python `random.choice()` แบบ 50/50
- ผลลัพธ์ถูกบันทึกทุกครั้ง (ไม่สามารถแก้ไขได้)

### 🔐 ความปลอดภัย
- ตรวจสอบ Authentication ทุก API
- Validate input ทุกครั้ง
- Transaction rollback เมื่อเกิดข้อผิดพลาด

## ตัวอย่างข้อมูล

### การเล่นที่ชนะ
```
user_id: 1
bet_amount: 100.00
selected_color: "blue"
result_color: "blue"
won: 1
win_loss_amount: +100.00
balance_before: 1000.00
balance_after: 1100.00
```

### การเล่นที่แพ้
```
user_id: 1
bet_amount: 50.00
selected_color: "white"
result_color: "blue"
won: 0
win_loss_amount: -50.00
balance_before: 1100.00
balance_after: 1050.00
```

## การ Debug และ Monitoring

### ดูข้อมูลในฐานข้อมูล
```sql
-- ดูการเล่นล่าสุด 10 ครั้ง
SELECT * FROM game1 ORDER BY played_at DESC LIMIT 10;

-- ดูสถิติผู้ใช้
SELECT * FROM game1_stats WHERE user_id = 1;

-- ดูผู้เล่นที่เล่นมากที่สุด
SELECT u.full_name, gs.total_games_played, gs.net_profit_loss 
FROM game1_stats gs 
JOIN users u ON gs.user_id = u.id 
ORDER BY gs.total_games_played DESC;
```

### การทดสอบ API
```bash
# ทดสอบการเล่นเกม
curl -X POST http://localhost:8000/api/game1/play \
  -H "Content-Type: application/json" \
  -H "Cookie: useremail=test@example.com" \
  -d '{"bet_amount": 100, "selected_color": "blue"}'

# ดูสถิติ
curl http://localhost:8000/api/game1/stats \
  -H "Cookie: useremail=test@example.com"
```

## Troubleshooting

### ปัญหาที่พบบ่อย

1. **"Insufficient balance"**
   - ตรวจสอบยอดเงินในตาราง `credit`
   - เติมเงินผ่าน API `/deposit`

2. **"User not found"**
   - ตรวจสอบว่า login แล้วและมี cookie `useremail`
   - ตรวจสอบว่า user มีอยู่ในตาราง `users`

3. **Trigger ไม่ทำงาน**
   - ตรวจสอบว่ารัน `create_game1_tables.sql` แล้ว
   - ดูใน PostgreSQL logs

4. **Permission denied**
   - ตรวจสอบ DB connection string
   - ตรวจสอบ user permissions ใน PostgreSQL

---

**สร้างโดย:** X-BET Development Team  
**อัปเดตล่าสุด:** 11 ตุลาคม 2025