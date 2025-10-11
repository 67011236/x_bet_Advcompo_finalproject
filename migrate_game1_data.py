"""
Migration script สำหรับอัพเดท Game1 data structure
ใช้เมื่อต้องการย้ายข้อมูลจากตารางเก่าไปตารางใหม่
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime

def migrate_game1_data():
    """
    Migrate ข้อมูลจากตาราง game1 เก่า (ถ้ามี) ไปยังโครงสร้างใหม่
    """
    
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'xbet_db'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password')
    }
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("🔗 Connected to PostgreSQL for migration")
        
        # 1. ตรวจสอบว่ามีตารางเก่าหรือไม่
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'game1'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("ℹ️  ไม่พบตาราง game1 เก่า - ไม่ต้อง migrate")
            return True
        
        # 2. ตรวจสอบโครงสร้างตารางเก่า
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'game1' 
            ORDER BY ordinal_position;
        """)
        
        old_columns = cursor.fetchall()
        old_column_names = [col[0] for col in old_columns]
        
        print(f"📋 ตารางเก่ามีคอลัมน์: {old_column_names}")
        
        # 3. ตรวจสอบว่าต้อง migrate หรือไม่
        required_columns = [
            'user_id', 'bet_amount', 'selected_color', 'result_color', 
            'won', 'balance_before', 'balance_after'
        ]
        
        missing_columns = [col for col in required_columns if col not in old_column_names]
        
        if missing_columns:
            print(f"🔧 ต้องเพิ่มคอลัมน์: {missing_columns}")
            
            # เพิ่มคอลัมน์ที่ขาดหาย
            if 'balance_before' in missing_columns:
                cursor.execute("ALTER TABLE game1 ADD COLUMN IF NOT EXISTS balance_before NUMERIC(10, 2) DEFAULT 0.00;")
                print("✅ เพิ่มคอลัมน์ balance_before")
            
            if 'balance_after' in missing_columns:
                cursor.execute("ALTER TABLE game1 ADD COLUMN IF NOT EXISTS balance_after NUMERIC(10, 2) DEFAULT 0.00;")
                print("✅ เพิ่มคอลัมน์ balance_after")
            
            if 'win_loss_amount' in missing_columns:
                cursor.execute("ALTER TABLE game1 ADD COLUMN IF NOT EXISTS win_loss_amount NUMERIC(10, 2);")
                print("✅ เพิ่มคอลัมน์ win_loss_amount")
        
        # 4. แปลง user_id จาก string เป็น integer (ถ้าจำเป็น)
        cursor.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'game1' AND column_name = 'user_id';
        """)
        
        user_id_type = cursor.fetchone()[0]
        
        if 'character' in user_id_type or 'text' in user_id_type:
            print("🔄 Converting user_id from string to integer...")
            
            # สร้างตารางใหม่ชั่วคราว
            cursor.execute("""
                CREATE TABLE game1_new AS 
                SELECT 
                    id,
                    CASE 
                        WHEN user_id ~ '^[0-9]+$' THEN user_id::integer
                        ELSE (
                            SELECT u.id FROM users u 
                            WHERE LOWER(u.email) = LOWER(game1.user_id) 
                            LIMIT 1
                        )
                    END as user_id,
                    bet_amount,
                    selected_color,
                    result_color,
                    won,
                    CASE 
                        WHEN won = 1 THEN bet_amount
                        ELSE -bet_amount 
                    END as win_loss_amount,
                    COALESCE(balance_before, 0.00) as balance_before,
                    COALESCE(balance_after, 0.00) as balance_after,
                    played_at
                FROM game1
                WHERE user_id IS NOT NULL;
            """)
            
            # ลบตารางเก่าและเปลี่ยนชื่อ
            cursor.execute("DROP TABLE game1;")
            cursor.execute("ALTER TABLE game1_new RENAME TO game1;")
            
            # เพิ่ม constraints และ indexes
            cursor.execute("ALTER TABLE game1 ADD PRIMARY KEY (id);")
            cursor.execute("ALTER TABLE game1 ADD FOREIGN KEY (user_id) REFERENCES users(id);")
            
            print("✅ แปลง user_id เป็น integer แล้ว")
        
        # 5. อัพเดท win_loss_amount ถ้ายังไม่มีค่า
        cursor.execute("""
            UPDATE game1 
            SET win_loss_amount = CASE 
                WHEN won = 1 THEN bet_amount 
                ELSE -bet_amount 
            END
            WHERE win_loss_amount IS NULL;
        """)
        
        # 6. สร้างสถิติใหม่จากข้อมูลที่มี
        print("📊 Creating initial statistics...")
        
        cursor.execute("""
            INSERT INTO game1_stats (
                user_id, total_games_played, total_wins, total_losses,
                total_bet_amount, total_win_amount, total_loss_amount,
                net_profit_loss, win_percentage, first_played_at, last_played_at
            )
            SELECT 
                user_id,
                COUNT(*) as total_games_played,
                COUNT(CASE WHEN won = 1 THEN 1 END) as total_wins,
                COUNT(CASE WHEN won = 0 THEN 1 END) as total_losses,
                SUM(bet_amount) as total_bet_amount,
                SUM(CASE WHEN won = 1 THEN bet_amount ELSE 0 END) as total_win_amount,
                SUM(CASE WHEN won = 0 THEN bet_amount ELSE 0 END) as total_loss_amount,
                SUM(CASE WHEN won = 1 THEN bet_amount ELSE -bet_amount END) as net_profit_loss,
                CASE 
                    WHEN COUNT(*) > 0 
                    THEN ROUND((COUNT(CASE WHEN won = 1 THEN 1 END) * 100.0 / COUNT(*)), 2)
                    ELSE 0 
                END as win_percentage,
                MIN(played_at) as first_played_at,
                MAX(played_at) as last_played_at
            FROM game1
            GROUP BY user_id
            ON CONFLICT (user_id) DO UPDATE SET
                total_games_played = EXCLUDED.total_games_played,
                total_wins = EXCLUDED.total_wins,
                total_losses = EXCLUDED.total_losses,
                total_bet_amount = EXCLUDED.total_bet_amount,
                total_win_amount = EXCLUDED.total_win_amount,
                total_loss_amount = EXCLUDED.total_loss_amount,
                net_profit_loss = EXCLUDED.net_profit_loss,
                win_percentage = EXCLUDED.win_percentage,
                first_played_at = EXCLUDED.first_played_at,
                last_played_at = EXCLUDED.last_played_at,
                updated_at = NOW();
        """)
        
        # 7. ดูผลลัพธ์
        cursor.execute("SELECT COUNT(*) FROM game1;")
        total_games = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM game1_stats;")
        total_users = cursor.fetchone()[0]
        
        print(f"✅ Migration completed:")
        print(f"   - Total games: {total_games}")
        print(f"   - Users with stats: {total_users}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def backup_existing_data():
    """
    สำรองข้อมูลเก่าก่อน migrate
    """
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'xbet_db'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password')
    }
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # สร้างตารางสำรอง
        backup_table = f"game1_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor.execute(f"""
            CREATE TABLE {backup_table} AS 
            SELECT * FROM game1;
        """)
        
        conn.commit()
        
        cursor.execute(f"SELECT COUNT(*) FROM {backup_table};")
        backup_count = cursor.fetchone()[0]
        
        print(f"✅ Backup created: {backup_table} ({backup_count} records)")
        
        return backup_table
        
    except Exception as e:
        print(f"❌ Backup error: {e}")
        return None
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 Game1 Data Migration Tool")
    print("=" * 50)
    
    # ตรวจสอบว่าต้องการสำรองข้อมูลหรือไม่
    backup_choice = input("💾 สำรองข้อมูลก่อน migrate? (y/n): ").lower()
    
    if backup_choice in ['y', 'yes', 'ใช่']:
        print("📦 Creating backup...")
        backup_table = backup_existing_data()
        if backup_table:
            print(f"✅ Backup successful: {backup_table}")
        else:
            print("❌ Backup failed, aborting migration")
            exit(1)
    
    # รัน migration
    print("🔄 Starting migration...")
    
    if migrate_game1_data():
        print("🎉 Migration completed successfully!")
    else:
        print("💥 Migration failed!")
        
        if backup_choice in ['y', 'yes', 'ใช่'] and backup_table:
            restore_choice = input("🔄 ต้องการ restore จาก backup หรือไม่? (y/n): ").lower()
            if restore_choice in ['y', 'yes', 'ใช่']:
                # Restore logic here
                print("🔄 Restore functionality can be implemented here")