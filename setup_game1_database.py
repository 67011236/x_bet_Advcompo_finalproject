"""
สคริปต์สำหรับสร้างตาราง game1 และ game1_stats ใน PostgreSQL
รันไฟล์นี้เพื่อสร้างตารางและ function/trigger ที่จำเป็น
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_game1_tables():
    """สร้างตาราง game1 และ game1_stats พร้อม functions และ triggers"""
    
    # ข้อมูลการเชื่อมต่อฐานข้อมูล
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'xbet_db'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password')
    }
    
    try:
        # เชื่อมต่อกับ PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("🔗 เชื่อมต่อกับ PostgreSQL สำเร็จ")
        
        # อ่านไฟล์ SQL
        with open('create_game1_tables.sql', 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # รัน SQL commands
        cursor.execute(sql_content)
        
        print("✅ สร้างตาราง game1 และ game1_stats สำเร็จ")
        print("✅ สร้าง functions และ triggers สำเร็จ")
        
        # ตรวจสอบว่าตารางถูกสร้างแล้ว
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('game1', 'game1_stats')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\n📋 ตารางที่สร้างแล้ว: {[table[0] for table in tables]}")
        
        # แสดงโครงสร้างตาราง game1
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'game1'
            ORDER BY ordinal_position
        """)
        
        game1_columns = cursor.fetchall()
        print("\n🎮 โครงสร้างตาราง game1:")
        for col in game1_columns:
            print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        
        # แสดงโครงสร้างตาราง game1_stats
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'game1_stats'
            ORDER BY ordinal_position
        """)
        
        stats_columns = cursor.fetchall()
        print("\n📊 โครงสร้างตาราง game1_stats:")
        for col in stats_columns:
            print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        
    except psycopg2.Error as e:
        print(f"❌ เกิดข้อผิดพลาดกับฐานข้อมูล: {e}")
        return False
        
    except FileNotFoundError:
        print("❌ ไม่พบไฟล์ create_game1_tables.sql")
        print("💡 กรุณาตรวจสอบว่าไฟล์ create_game1_tables.sql อยู่ในโฟลเดอร์เดียวกัน")
        return False
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        print("\n🔐 ปิดการเชื่อมต่อฐานข้อมูลแล้ว")
    
    return True

def test_game1_functionality():
    """ทดสอบการทำงานของตาราง game1"""
    
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
        
        print("\n🧪 ทดสอบการทำงานของตาราง game1...")
        
        # ตรวจสอบว่ามี user ในระบบหรือไม่
        cursor.execute("SELECT id, full_name FROM users LIMIT 1")
        user = cursor.fetchone()
        
        if not user:
            print("⚠️  ไม่พบผู้ใช้ในระบบ กรุณาสร้างผู้ใช้ก่อน")
            return False
            
        user_id = user[0]
        user_name = user[1]
        print(f"👤 ใช้ผู้ใช้ทดสอบ: {user_name} (ID: {user_id})")
        
        # เพิ่มข้อมูลทดสอบ
        test_data = [
            (user_id, 100.00, 'blue', 'blue', 1, 100.00, 1000.00, 1100.00),
            (user_id, 50.00, 'white', 'blue', 0, -50.00, 1100.00, 1050.00),
            (user_id, 200.00, 'blue', 'white', 0, -200.00, 1050.00, 850.00),
        ]
        
        for data in test_data:
            cursor.execute("""
                INSERT INTO game1 (user_id, bet_amount, selected_color, result_color, 
                                  won, win_loss_amount, balance_before, balance_after) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, data)
        
        print("✅ เพิ่มข้อมูลทดสอบ 3 รายการ")
        
        # ตรวจสอบข้อมูลในตาราง game1
        cursor.execute("""
            SELECT COUNT(*) as total_games,
                   SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END) as wins,
                   SUM(bet_amount) as total_bet,
                   SUM(win_loss_amount) as net_result
            FROM game1 WHERE user_id = %s
        """, (user_id,))
        
        game_summary = cursor.fetchone()
        print(f"🎮 สรุปการเล่น: {game_summary[0]} เกม, ชนะ {game_summary[1]} ครั้ง")
        print(f"💰 เดิมพันรวม: {game_summary[2]} บาท, ผลรวม: {game_summary[3]} บาท")
        
        # ตรวจสอบข้อมูลในตาราง game1_stats (จะถูก trigger อัพเดทอัตโนมัติ)
        cursor.execute("""
            SELECT total_games_played, total_wins, total_losses,
                   net_profit_loss, win_percentage
            FROM game1_stats WHERE user_id = %s
        """, (user_id,))
        
        stats = cursor.fetchone()
        if stats:
            print(f"📊 สถิติอัตโนมัติ: เล่น {stats[0]} ครั้ง, ชนะ {stats[1]}, แพ้ {stats[2]}")
            print(f"💹 กำไร/ขาดทุน: {stats[3]} บาท, เปอร์เซ็นต์ชนะ: {stats[4]}%")
        else:
            print("⚠️  ไม่พบข้อมูลสถิติ (อาจจะ trigger ไม่ทำงาน)")
        
        print("\n✅ การทดสอบเสร็จสิ้น")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการทดสอบ: {e}")
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    return True

if __name__ == "__main__":
    print("🚀 เริ่มต้นการสร้างตาราง game1 สำหรับ X-BET")
    print("=" * 50)
    
    # สร้างตาราง
    if create_game1_tables():
        print("\n" + "=" * 50)
        
        # ถามว่าต้องการทดสอบหรือไม่
        while True:
            test_choice = input("\n❓ ต้องการทดสอบการทำงานของตารางหรือไม่? (y/n): ").lower()
            if test_choice in ['y', 'yes', 'ใช่']:
                test_game1_functionality()
                break
            elif test_choice in ['n', 'no', 'ไม่']:
                print("✅ การสร้างตารางเสร็จสิ้น")
                break
            else:
                print("กรุณาตอบ y หรือ n")
    
    print("\n🎉 ขอบคุณที่ใช้งาน!")