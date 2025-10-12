# Game2 (Rock Paper Scissors) Database Setup

## 📋 ข้อมูลที่เก็บใน Game2 Database

### 1. Table: `game2` (เก็บข้อมูลการเล่นแต่ละครั้ง)

| Field | Type | Description |
|-------|------|-------------|
| `id` | INTEGER | Primary key |
| `user_id` | INTEGER | Foreign key ไปยัง users table |
| `bet_amount` | DECIMAL(10,2) | จำนวนเงินที่เดิมพัน |
| `player_choice` | VARCHAR(10) | ตัวเลือกของผู้เล่น (rock, paper, scissors) |
| `bot_choice` | VARCHAR(10) | ตัวเลือกของบอท (rock, paper, scissors) |
| `result` | VARCHAR(10) | ผลลัพธ์ (win, lose, tie) |
| `win_loss_amount` | DECIMAL(10,2) | จำนวนเงินที่ชนะ/แพ้ (+100, -100, 0) |
| `balance_before` | DECIMAL(10,2) | ยอดเงินก่อนเล่น |
| `balance_after` | DECIMAL(10,2) | ยอดเงินหลังเล่น |
| `played_at` | DATETIME | เวลาที่เล่น |

### 2. Table: `game2_stats` (เก็บสถิติรวมของแต่ละผู้ใช้)

| Field | Type | Description |
|-------|------|-------------|
| `id` | INTEGER | Primary key |
| `user_id` | INTEGER | Foreign key ไปยัง users table (unique) |
| `total_games_played` | INTEGER | จำนวนครั้งที่เล่นทั้งหมด |
| `total_wins` | INTEGER | จำนวนครั้งที่ชนะ |
| `total_losses` | INTEGER | จำนวนครั้งที่แพ้ |
| `total_ties` | INTEGER | จำนวนครั้งที่เสมอ |
| `total_bet_amount` | DECIMAL(15,2) | ยอดเดิมพันรวม |
| `total_win_amount` | DECIMAL(15,2) | ยอดเงินที่ชนะรวม |
| `total_loss_amount` | DECIMAL(15,2) | ยอดเงินที่แพ้รวม |
| `net_profit_loss` | DECIMAL(15,2) | กำไร/ขาดทุนสุทธิ |
| `rock_played` | INTEGER | จำนวนครั้งที่เลือก Rock |
| `paper_played` | INTEGER | จำนวนครั้งที่เลือก Paper |
| `scissors_played` | INTEGER | จำนวนครั้งที่เลือก Scissors |
| `first_played_at` | DATETIME | วันที่เล่นครั้งแรก |
| `last_played_at` | DATETIME | วันที่เล่นครั้งล่าสุด |

## 🚀 วิธีการ Setup

### 1. สร้าง Database Tables

```bash
# รัน script setup อัตโนมัติ
python setup_game2_database.py

# หรือรัน SQL manual ใน DBeaver
# ใช้ไฟล์: create_game2_tables.sql
```

### 2. รัน Backend Server

```bash
cd backend
pip install -r requirements.txt
python -m app.main
```

### 3. รัน Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. เปิดเกม

เข้า: `http://localhost:3000/game2`

## 📊 ตัวอย่าง SQL Queries สำหรับดูข้อมูล

### ดูการเล่นล่าสุด 10 รอบ
```sql
SELECT 
    g.id,
    u.full_name,
    u.email,
    g.bet_amount,
    g.player_choice,
    g.bot_choice,
    g.result,
    g.win_loss_amount,
    g.balance_after,
    g.played_at
FROM game2 g
JOIN users u ON g.user_id = u.id
ORDER BY g.played_at DESC
LIMIT 10;
```

### ดูสถิติของ user ทั้งหมด
```sql
SELECT 
    u.full_name,
    u.email,
    s.total_games_played,
    s.total_wins,
    s.total_losses,
    s.total_ties,
    ROUND((s.total_wins * 100.0 / s.total_games_played), 2) as win_percentage,
    s.net_profit_loss,
    s.rock_played,
    s.paper_played,
    s.scissors_played
FROM game2_stats s
JOIN users u ON s.user_id = u.id
ORDER BY s.total_games_played DESC;
```

### ดูการเล่นของ user คนใดคนหนึ่ง
```sql
SELECT 
    bet_amount,
    player_choice,
    bot_choice,
    result,
    win_loss_amount,
    balance_before,
    balance_after,
    played_at
FROM game2 
WHERE user_id = 1  -- เปลี่ยนเป็น user_id ที่ต้องการดู
ORDER BY played_at DESC
LIMIT 20;
```

## 🔗 API Endpoints

### POST `/api/game2/play`
เล่นเกม Rock Paper Scissors

**Request:**
```json
{
  "bet_amount": 100,
  "player_choice": "rock",
  "bot_choice": "scissors",
  "result": "win"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "game_id": 123,
    "player_choice": "rock",
    "bot_choice": "scissors",
    "result": "win",
    "bet_amount": 100,
    "win_loss_amount": 200,
    "balance_before": 500,
    "balance_after": 600,
    "message": "You win!"
  }
}
```

### GET `/api/game2/history`
ดึงประวัติการเล่น

**Query Parameters:**
- `limit`: จำนวนรายการ (default: 20)
- `offset`: เริ่มจากรายการที่ (default: 0)

### GET `/api/game2/stats`
ดึงสถิติการเล่น

## 💡 การทำงานของระบบ

1. **ผู้ใช้เล่นเกม**: เลือก Rock/Paper/Scissors และใส่จำนวนเดิมพัน
2. **บันทึกข้อมูล**: เมื่อเล่นเสร็จ ระบบจะบันทึกลง `game2` table
3. **อัพเดทสถิติ**: อัพเดท `game2_stats` table อัตโนมัติ
4. **อัพเดทยอดเงิน**: อัพเดทยอดเงินใน `credit` table
5. **แสดงผล**: ส่งผลลัพธ์กลับไปยัง Frontend

## 🎯 จุดเด่นของระบบ

- ✅ **เก็บข้อมูลครบถ้วน**: ทั้งการเล่นแต่ละครั้งและสถิติรวม
- ✅ **Real-time Updates**: อัพเดทยอดเงินและสถิติทันที
- ✅ **Data Integrity**: ใช้ Foreign Keys และ Constraints
- ✅ **Performance**: มี Indexes สำหรับ query ที่เร็ว
- ✅ **Scalable**: ออกแบบให้รองรับผู้ใช้หลายคน

## 🛠️ การใช้งาน DBeaver

1. **เชื่อมต่อ Database**: เปิด `dev.db` ใน DBeaver
2. **ดูข้อมูล**: เรียกใช้ SQL queries ข้างบน
3. **วิเคราะห์**: ใช้ charts และ reports ใน DBeaver
4. **Export**: ส่งออกข้อมูลเป็น Excel, CSV ได้

ตอนนี้คุณสามารถเชื่อมต่อหน้า Game2 กับฐานข้อมูลได้แล้ว! 🎮✨