#!/usr/bin/env python3
"""
Setup Game2 Database
สร้าง tables และ setup database สำหรับ Game2 (Rock Paper Scissors)
"""

import os
import sys
import sqlite3
from datetime import datetime

def setup_game2_database():
    """สร้าง database และ tables สำหรับ Game2"""
    
    # กำหนดที่อยู่ database file
    db_path = "dev.db"  # ใช้ชื่อเดียวกับ backend
    
    print("🔧 Setting up Game2 database...")
    
    try:
        # เชื่อมต่อ SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"📁 Connected to database: {db_path}")
        
        # สร้าง Game2 table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                bet_amount DECIMAL(10,2) NOT NULL CHECK (bet_amount > 0),
                player_choice VARCHAR(10) NOT NULL CHECK (player_choice IN ('rock','paper','scissors')),
                bot_choice VARCHAR(10) NOT NULL CHECK (bot_choice IN ('rock','paper','scissors')),
                result VARCHAR(10) NOT NULL CHECK (result IN ('win','lose','tie')),
                win_loss_amount DECIMAL(10,2) NOT NULL,
                balance_before DECIMAL(10,2) NOT NULL,
                balance_after DECIMAL(10,2) NOT NULL,
                played_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        print("✅ Table 'game2' created successfully")
        
        # สร้าง Game2 Stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game2_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                total_games_played INTEGER NOT NULL DEFAULT 0,
                total_wins INTEGER NOT NULL DEFAULT 0,
                total_losses INTEGER NOT NULL DEFAULT 0,
                total_ties INTEGER NOT NULL DEFAULT 0,
                total_bet_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00,
                total_win_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00,
                total_loss_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00,
                net_profit_loss DECIMAL(15,2) NOT NULL DEFAULT 0.00,
                rock_played INTEGER NOT NULL DEFAULT 0,
                paper_played INTEGER NOT NULL DEFAULT 0,
                scissors_played INTEGER NOT NULL DEFAULT 0,
                first_played_at DATETIME,
                last_played_at DATETIME,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        print("✅ Table 'game2_stats' created successfully")
        
        # สร้าง indexes สำหรับ performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_game2_user_id ON game2(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_game2_played_at ON game2(played_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_game2_result ON game2(result)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_game2_stats_user_id ON game2_stats(user_id)')
        print("✅ Indexes created successfully")
        
        # Commit changes
        conn.commit()
        
        # ตรวจสอบว่า tables ถูกสร้างแล้ว
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('game2', 'game2_stats')")
        tables = cursor.fetchall()
        
        print(f"\n📊 Created tables: {[table[0] for table in tables]}")
        
        # แสดงจำนวนข้อมูลในตาราง
        cursor.execute("SELECT COUNT(*) FROM game2")
        game2_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM game2_stats")
        stats_count = cursor.fetchone()[0]
        
        print(f"📈 Current data:")
        print(f"   - game2 records: {game2_count}")
        print(f"   - game2_stats records: {stats_count}")
        
        # ตรวจสอบ users table ว่ามีข้อมูลไหม
        try:
            cursor.execute("SELECT COUNT(*) FROM users")
            users_count = cursor.fetchone()[0]
            print(f"   - users records: {users_count}")
            
            if users_count > 0:
                cursor.execute("SELECT id, full_name, email FROM users LIMIT 3")
                users = cursor.fetchall()
                print("   - Sample users:")
                for user in users:
                    print(f"     • ID: {user[0]}, Name: {user[1]}, Email: {user[2]}")
        except sqlite3.OperationalError:
            print("   - users table not found (will be created by backend)")
        
        conn.close()
        print(f"\n🎮 Game2 database setup completed!")
        print(f"📍 Database file: {os.path.abspath(db_path)}")
        print("\n🚀 You can now run the backend server and play Game2!")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def check_database_status():
    """ตรวจสอบสถานะของ database"""
    db_path = "dev.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ตรวจสอบว่ามี tables หรือไม่
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📊 Available tables: {tables}")
        
        if 'game2' in tables and 'game2_stats' in tables:
            print("✅ Game2 tables are ready!")
            return True
        else:
            print("❌ Game2 tables not found")
            return False
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    print("🎮 Game2 Database Setup Tool")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        # ตรวจสอบสถานะเท่านั้น
        check_database_status()
    else:
        # Setup database
        success = setup_game2_database()
        
        if success:
            print("\n" + "=" * 50)
            print("✅ Setup completed successfully!")
            print("🔗 Next steps:")
            print("   1. Start the backend server: cd backend && python -m app.main")
            print("   2. Start the frontend: cd frontend && npm run dev")
            print("   3. Open http://localhost:3000/game2 to play!")
        else:
            print("\n" + "=" * 50)
            print("❌ Setup failed!")
            sys.exit(1)