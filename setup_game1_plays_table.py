#!/usr/bin/env python3
"""
Script to create game1_plays table for tracking game statistics
"""
import sqlite3
import os

def create_game1_plays_table():
    # Path to the database
    db_path = "backend/dev.db"
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create game1_plays table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game1_plays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                bet_amount INTEGER NOT NULL,
                selected_color TEXT NOT NULL,
                result_color TEXT NOT NULL,
                won BOOLEAN NOT NULL,
                payout INTEGER NOT NULL,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES credit (user_id)
            )
        ''')
        
        # Create index for better performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_game1_plays_user_id 
            ON game1_plays(user_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_game1_plays_played_at 
            ON game1_plays(played_at)
        ''')
        
        # Commit changes
        conn.commit()
        print("✅ game1_plays table created successfully!")
        
        # Show table structure
        cursor.execute("PRAGMA table_info(game1_plays)")
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

if __name__ == "__main__":
    print("🎮 Setting up game1_plays table...")
    success = create_game1_plays_table()
    
    if success:
        print("\n🎯 Table setup completed successfully!")
        print("Now you can track game statistics in DBeaver!")
    else:
        print("\n💥 Failed to set up table!")