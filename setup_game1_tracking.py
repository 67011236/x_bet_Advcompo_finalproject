#!/usr/bin/env python3
"""
Script to create/update database tables including the new game1 table
"""
import sqlite3
import os
import sys

def create_game1_table():
    # Path to the database
    db_path = "backend/dev.db"
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        print("Please make sure the backend server has been started at least once.")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if game1 table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='game1'
        """)
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            print("✅ Table 'game1' already exists!")
            
            # Show current structure
            cursor.execute("PRAGMA table_info(game1)")
            columns = cursor.fetchall()
            print("\n📋 Current Table Structure:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Show current data count
            cursor.execute("SELECT COUNT(*) FROM game1")
            count = cursor.fetchone()[0]
            print(f"\n📊 Current records: {count}")
            
            if count > 0:
                print("\n🎮 Latest 5 records:")
                cursor.execute("""
                    SELECT id, user_id, bet_amount, selected_color, result_color, won, payout_amount, played_at 
                    FROM game1 
                    ORDER BY played_at DESC 
                    LIMIT 5
                """)
                records = cursor.fetchall()
                for record in records:
                    print(f"  ID:{record[0]} | User:{record[1]} | Bet:{record[2]} | {record[3]}→{record[4]} | {'WIN' if record[5] else 'LOSE'} | {record[6]:+d} | {record[7]}")
        else:
            # Create game1 table
            print("🔨 Creating table 'game1'...")
            cursor.execute('''
                CREATE TABLE game1 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    bet_amount INTEGER NOT NULL,
                    selected_color TEXT NOT NULL CHECK (selected_color IN ('blue','white')),
                    result_color TEXT NOT NULL CHECK (result_color IN ('blue','white')),
                    won INTEGER NOT NULL CHECK (won IN (0,1)),
                    payout_amount INTEGER NOT NULL,
                    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CHECK (bet_amount > 0)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('''
                CREATE INDEX idx_game1_user_id ON game1(user_id)
            ''')
            
            cursor.execute('''
                CREATE INDEX idx_game1_played_at ON game1(played_at)
            ''')
            
            # Commit changes
            conn.commit()
            print("✅ Table 'game1' created successfully!")
            
            # Show table structure
            cursor.execute("PRAGMA table_info(game1)")
            columns = cursor.fetchall()
            print("\n📋 Table Structure:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_backend_connection():
    """Test if backend is running and API is accessible"""
    try:
        import requests
        
        print("\n🔗 Testing backend connection...")
        
        # Test basic endpoint
        response = requests.get("http://localhost:8000/api/dashboard-stats", timeout=5)
        
        if response.status_code == 401:
            print("✅ Backend is running (authentication required as expected)")
            return True
        elif response.status_code == 200:
            print("✅ Backend is running and accessible")
            return True
        else:
            print(f"⚠️ Backend responded with status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend not running. Please start with: docker compose up")
        return False
    except ImportError:
        print("⚠️ requests library not installed. Cannot test backend connection.")
        return True
    except Exception as e:
        print(f"⚠️ Error testing backend: {e}")
        return True

if __name__ == "__main__":
    print("🎮 Setting up Game1 tracking system...")
    print("="*50)
    
    # Test backend connection first
    backend_running = test_backend_connection()
    
    # Create/check game1 table
    success = create_game1_table()
    
    print("\n" + "="*50)
    if success:
        print("🎯 Setup completed!")
        if backend_running:
            print("\n📝 Instructions:")
            print("1. Make sure backend is running: docker compose up")
            print("2. Access the game at: http://localhost:3000/game1")
            print("3. Play a few rounds")
            print("4. Check DBeaver to see the recorded data!")
        else:
            print("\n⚠️ Next steps:")
            print("1. Start backend: docker compose up")
            print("2. Run this script again to verify")
    else:
        print("💥 Setup failed!")
        sys.exit(1)