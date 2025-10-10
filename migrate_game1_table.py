#!/usr/bin/env python3
"""
Database migration script to create/update game1 table in PostgreSQL
"""
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def get_db_connection():
    """Get database connection using environment variables"""
    try:
        # Try to get PostgreSQL connection (for Docker)
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "xbet_db"),
            user=os.getenv("DB_USER", "xbet_user"),
            password=os.getenv("DB_PASSWORD", "xbet_pass")
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn, "postgresql"
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")
        
        # Fallback to SQLite
        try:
            import sqlite3
            conn = sqlite3.connect("backend/dev.db")
            conn.execute("PRAGMA foreign_keys = ON")
            return conn, "sqlite"
        except Exception as e2:
            print(f"SQLite connection failed: {e2}")
            return None, None

def create_or_update_game1_table():
    """Create or update game1 table"""
    conn, db_type = get_db_connection()
    
    if not conn:
        print("❌ Failed to connect to database!")
        return False
    
    try:
        cursor = conn.cursor()
        
        if db_type == "postgresql":
            # Check if table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'game1'
                )
            """)
            table_exists = cursor.fetchone()[0]
            
            if table_exists:
                print("✅ Table 'game1' exists in PostgreSQL")
                
                # Check columns
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'game1' 
                    AND table_schema = 'public'
                """)
                columns = [row[0] for row in cursor.fetchall()]
                print(f"📋 Current columns: {columns}")
                
                # Check if we need to add missing columns
                required_columns = [
                    'id', 'user_id', 'bet_amount', 'selected_color', 
                    'result_color', 'won', 'payout_amount', 'played_at'
                ]
                
                missing_columns = [col for col in required_columns if col not in columns]
                
                if missing_columns:
                    print(f"🔧 Adding missing columns: {missing_columns}")
                    
                    column_definitions = {
                        'user_id': 'TEXT NOT NULL',
                        'bet_amount': 'INTEGER NOT NULL',
                        'selected_color': 'TEXT NOT NULL CHECK (selected_color IN (\'blue\',\'white\'))',
                        'result_color': 'TEXT NOT NULL CHECK (result_color IN (\'blue\',\'white\'))',
                        'won': 'INTEGER NOT NULL CHECK (won IN (0,1))',
                        'payout_amount': 'INTEGER NOT NULL',
                        'played_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
                    }
                    
                    for col in missing_columns:
                        if col in column_definitions:
                            try:
                                cursor.execute(f"""
                                    ALTER TABLE game1 
                                    ADD COLUMN {col} {column_definitions[col]}
                                """)
                                print(f"  ✅ Added column: {col}")
                            except Exception as e:
                                print(f"  ⚠️ Failed to add {col}: {e}")
                else:
                    print("✅ All required columns exist")
            else:
                print("🔨 Creating table 'game1' in PostgreSQL...")
                cursor.execute("""
                    CREATE TABLE game1 (
                        id SERIAL PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        bet_amount INTEGER NOT NULL CHECK (bet_amount > 0),
                        selected_color TEXT NOT NULL CHECK (selected_color IN ('blue','white')),
                        result_color TEXT NOT NULL CHECK (result_color IN ('blue','white')),
                        won INTEGER NOT NULL CHECK (won IN (0,1)),
                        payout_amount INTEGER NOT NULL,
                        played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes
                cursor.execute("CREATE INDEX idx_game1_user_id ON game1(user_id)")
                cursor.execute("CREATE INDEX idx_game1_played_at ON game1(played_at)")
                
                print("✅ Table 'game1' created successfully!")
        
        elif db_type == "sqlite":
            print("🔧 Working with SQLite database...")
            # SQLite logic (similar to before)
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='game1'
            """)
            table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                cursor.execute('''
                    CREATE TABLE game1 (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        bet_amount INTEGER NOT NULL CHECK (bet_amount > 0),
                        selected_color TEXT NOT NULL CHECK (selected_color IN ('blue','white')),
                        result_color TEXT NOT NULL CHECK (result_color IN ('blue','white')),
                        won INTEGER NOT NULL CHECK (won IN (0,1)),
                        payout_amount INTEGER NOT NULL,
                        played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                cursor.execute("CREATE INDEX idx_game1_user_id ON game1(user_id)")
                cursor.execute("CREATE INDEX idx_game1_played_at ON game1(played_at)")
                
                conn.commit()
                print("✅ SQLite table 'game1' created successfully!")
        
        # Show final table info
        if db_type == "postgresql":
            cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'game1' 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            print("\n📋 Final table structure:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
                
            # Show record count
            cursor.execute("SELECT COUNT(*) FROM game1")
            count = cursor.fetchone()[0]
            print(f"\n📊 Current records: {count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    print("🎮 Game1 Database Migration")
    print("="*40)
    
    success = create_or_update_game1_table()
    
    print("\n" + "="*40)
    if success:
        print("🎯 Migration completed successfully!")
        print("\n📝 Next steps:")
        print("1. Start the application: docker compose up")
        print("2. Play the game: http://localhost:3000/game1")
        print("3. Check DBeaver for recorded data")
    else:
        print("💥 Migration failed!")
        print("Please check the error messages above.")