#!/usr/bin/env python3
"""
Setup All Tables - สร้าง tables ทั้งหมดสำหรับ SQLite
"""

import sqlite3
import os

def setup_all_tables():
    """สร้าง tables ทั้งหมด"""
    
    db_path = "dev.db"
    
    print("🔧 Setting up all tables for SQLite...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"📁 Connected to database: {db_path}")
        
        # Create Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name VARCHAR(120) NOT NULL,
                age INTEGER NOT NULL CHECK (age >= 20),
                phone VARCHAR(20) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('user','admin')),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Table 'users' created")
        
        # Create Credit table  
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                balance DECIMAL(15,2) NOT NULL DEFAULT 0.00 CHECK (balance >= 0),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        print("✅ Table 'credit' created")
        
        # Create Reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title VARCHAR(255) NOT NULL,
                category VARCHAR(50) NOT NULL CHECK (category IN ('technical','payment','account','betting','suggestion','other')),
                description TEXT NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','reviewing','resolved','closed')),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        print("✅ Table 'reports' created")
        
        # Create Game1 table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game1 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                bet_amount DECIMAL(10,2) NOT NULL CHECK (bet_amount > 0),
                selected_color VARCHAR(10) NOT NULL CHECK (selected_color IN ('blue','white')),
                result_color VARCHAR(10) NOT NULL CHECK (result_color IN ('blue','white')),
                won INTEGER NOT NULL CHECK (won IN (0,1)),
                win_loss_amount DECIMAL(10,2) NOT NULL,
                balance_before DECIMAL(10,2) NOT NULL,
                balance_after DECIMAL(10,2) NOT NULL,
                played_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        print("✅ Table 'game1' created")
        
        # Create Game2 table
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
        print("✅ Table 'game2' created")
        
        # Create Game2 Stats table
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
        print("✅ Table 'game2_stats' created")
        
        # สร้าง sample users
        print("\n👤 Creating sample users...")
        
        # Admin user
        cursor.execute('''
            INSERT OR IGNORE INTO users (full_name, age, phone, email, password_hash, role)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ("Admin User", 30, "0000000000", "admin@xbet.com", "$2b$12$example_admin_hash", "admin"))
        
        # Test user  
        cursor.execute('''
            INSERT OR IGNORE INTO users (full_name, age, phone, email, password_hash, role)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ("Test User", 25, "0812345678", "test1234@gmail.com", "$2b$12$example_test_hash", "user"))
        
        print("✅ Sample users created")
        
        # สร้าง sample credit
        cursor.execute("SELECT id FROM users WHERE email = 'admin@xbet.com'")
        admin_user = cursor.fetchone()
        if admin_user:
            cursor.execute('''
                INSERT OR IGNORE INTO credit (user_id, balance) 
                VALUES (?, ?)
            ''', (admin_user[0], 1000000.00))
        
        cursor.execute("SELECT id FROM users WHERE email = 'test1234@gmail.com'")
        test_user = cursor.fetchone()
        if test_user:
            cursor.execute('''
                INSERT OR IGNORE INTO credit (user_id, balance) 
                VALUES (?, ?)
            ''', (test_user[0], 50.00))
        
        print("✅ Sample credit balances created")
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_game1_user_id ON game1(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_game1_played_at ON game1(played_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_game2_user_id ON game2(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_game2_played_at ON game2(played_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports(user_id)')
        print("✅ Indexes created")
        
        conn.commit()
        
        # ตรวจสอบ tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\n📊 All tables: {tables}")
        
        # ตรวจสอบจำนวนข้อมูล
        for table in ['users', 'credit', 'game1', 'game2', 'game2_stats', 'reports']:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   • {table}: {count} records")
        
        conn.close()
        
        print(f"\n🎉 All tables setup completed!")
        print(f"📍 Database file: {os.path.abspath(db_path)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🛠️  Complete Database Setup")
    print("=" * 50)
    
    success = setup_all_tables()
    
    if success:
        print("\n✅ Ready to use!")
        print("🔗 Next steps:")
        print("   1. Run backend: cd backend && python -m app.main")  
        print("   2. Run frontend: cd frontend && npm run dev")
        print("   3. Open dashboard: http://localhost:3000/dashboard")
    else:
        print("\n❌ Setup failed!")