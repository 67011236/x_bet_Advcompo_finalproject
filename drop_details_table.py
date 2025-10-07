#!/usr/bin/env python3
"""
Script สำหรับลบ table 'details' ออกจากฐานข้อมูล
"""

import sqlite3
import os

def drop_details_table():
    """ลบ table 'details' ออกจากฐานข้อมูล"""
    
    # เชื่อมต่อฐานข้อมูล
    db_path = os.path.join("backend", "dev.db")
    
    if not os.path.exists(db_path):
        print(f"❌ ไม่พบไฟล์ฐานข้อมูล: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ตรวจสอบว่ามี table details อยู่หรือไม่
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='details'")
        details_exists = cursor.fetchone()
        
        if not details_exists:
            print("ℹ️  ไม่พบ table 'details' ในฐานข้อมูล")
            return True
        
        # ตรวจสอบข้อมูลใน details table ก่อนลบ
        cursor.execute("SELECT COUNT(*) as count FROM details")
        record_count = cursor.fetchone()[0]
        
        if record_count > 0:
            print(f"⚠️  Table 'details' มี {record_count} records")
            print("📊 ข้อมูลในตาราง:")
            cursor.execute("SELECT * FROM details")
            records = cursor.fetchall()
            for record in records:
                print(f"   - {record}")
            
            response = input(f"\nคุณแน่ใจหรือไม่ที่จะลบ table 'details' และข้อมูลทั้งหมด? (y/N): ")
            if response.lower() != 'y':
                print("❌ ยกเลิกการลบ table")
                return False
        else:
            print("📝 Table 'details' ไม่มีข้อมูล")
            response = input("คุณต้องการลบ table 'details' หรือไม่? (y/N): ")
            if response.lower() != 'y':
                print("❌ ยกเลิกการลบ table")
                return False
        
        # ลบ table details
        print("🗑️  กำลังลบ table 'details'...")
        cursor.execute("DROP TABLE details")
        conn.commit()
        
        print("✅ ลบ table 'details' สำเร็จ!")
        
        # ตรวจสอบ tables ที่เหลือ
        print("\n📊 Tables ที่เหลือในฐานข้อมูล:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        remaining_tables = cursor.fetchall()
        
        for table in remaining_tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   - {table_name}: {count} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🗑️  Drop Table Tool: ลบ table 'details'")
    print("=" * 50)
    
    success = drop_details_table()
    
    if success:
        print("\n✅ การลบ table เสร็จสิ้น!")
        print("💡 ระบบจะใช้ table 'credit' ในการเก็บข้อมูล balance")
    else:
        print("\n❌ การลบ table ล้มเหลว")