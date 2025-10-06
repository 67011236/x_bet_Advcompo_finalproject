#!/usr/bin/env python3
"""
Simple Migration script: ย้ายข้อมูลจาก table 'details' ไปยัง table 'credit'
วิธีใช้: python check_and_migrate.py
"""

import sqlite3
import os
from decimal import Decimal
from datetime import datetime

def migrate_details_to_credit():
    """ย้ายข้อมูลจาก details table ไปยัง credit table"""
    
    # เชื่อมต่อฐานข้อมูล
    db_path = os.path.join("backend", "dev.db")
    
    if not os.path.exists(db_path):
        print(f"❌ ไม่พบไฟล์ฐานข้อมูล: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # ให้สามารถเข้าถึงข้อมูลแบบ dict ได้
        cursor = conn.cursor()
        
        print("🔍 ตรวจสอบ tables ที่มีอยู่...")
        
        # ตรวจสอบว่ามี table details อยู่หรือไม่
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='details'")
        details_exists = cursor.fetchone()
        
        if not details_exists:
            print("❌ ไม่พบ table 'details' ในฐานข้อมูล")
            return False
        
        # ตรวจสอบว่ามี table credit อยู่หรือไม่
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='credit'")
        credit_exists = cursor.fetchone()
        
        if not credit_exists:
            print("❌ ไม่พบ table 'credit' ในฐานข้อมูล")
            print("💡 กรุณารัน backend server ก่อนเพื่อสร้าง table 'credit'")
            return False
        
        print("✅ พบทั้ง table 'details' และ 'credit'")
        
        # ดึงข้อมูลจาก details table
        print("\n🔍 ตรวจสอบข้อมูลใน table 'details'...")
        cursor.execute("SELECT * FROM details")
        details_records = cursor.fetchall()
        
        if not details_records:
            print("📝 ไม่พบข้อมูลใน table 'details'")
            return True
        
        print(f"📊 พบข้อมูล {len(details_records)} records ใน table 'details':")
        for record in details_records:
            print(f"   - user_id: {record['user_id']}, balance: {record['balance']}")
        
        # ตรวจสอบว่ามีข้อมูลใน credit table อยู่แล้วหรือไม่
        cursor.execute("SELECT COUNT(*) as count FROM credit")
        credit_count = cursor.fetchone()['count']
        
        if credit_count > 0:
            print(f"\n⚠️  Table 'credit' มีข้อมูล {credit_count} records อยู่แล้ว")
            response = input("คุณต้องการเขียนทับข้อมูลเดิมหรือไม่? (y/N): ")
            if response.lower() != 'y':
                print("❌ ยกเลิกการ migrate")
                return False
            
            # ลบข้อมูลเดิมใน credit table
            cursor.execute("DELETE FROM credit")
            print("🗑️  ลบข้อมูลเดิมใน table 'credit' แล้ว")
        
        # ย้ายข้อมูลจาก details ไปยัง credit
        print("\n📦 เริ่มย้ายข้อมูล...")
        
        migrated_count = 0
        current_time = datetime.utcnow().isoformat()
        
        for record in details_records:
            try:
                user_id = record['user_id']
                balance = record['balance'] if record['balance'] else 0.00
                created_at = record.get('created_at', current_time)
                updated_at = record.get('updated_at', current_time)
                
                # ตรวจสอบว่า user_id มีอยู่ใน users table หรือไม่
                cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
                user_exists = cursor.fetchone()
                
                if not user_exists:
                    print(f"⚠️  ข้าม user_id {user_id} (ไม่พบใน users table)")
                    continue
                
                # Insert ข้อมูลลงใน credit table
                cursor.execute("""
                    INSERT INTO credit (user_id, balance, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (user_id, balance, created_at, updated_at))
                
                migrated_count += 1
                print(f"✅ ย้ายข้อมูล user_id: {user_id}, balance: {balance}")
                
            except Exception as e:
                print(f"❌ Error ย้ายข้อมูล user_id {record['user_id']}: {e}")
                continue
        
        # Commit การเปลี่ยนแปลง
        conn.commit()
        print(f"\n🎉 Migration สำเร็จ! ย้ายข้อมูล {migrated_count}/{len(details_records)} records")
        
        # ตรวจสอบข้อมูลใน credit table
        print("\n🔍 ตรวจสอบข้อมูลใน table 'credit' หลัง migration:")
        cursor.execute("SELECT * FROM credit")
        credit_records = cursor.fetchall()
        for record in credit_records:
            print(f"   - user_id: {record['user_id']}, balance: {record['balance']}")
        
        # ถามว่าต้องการลบ details table หรือไม่
        print(f"\n📝 Table 'details' ยังคงมีอยู่ ({len(details_records)} records)")
        response = input("คุณต้องการลบ table 'details' หรือไม่? (y/N): ")
        if response.lower() == 'y':
            cursor.execute("DROP TABLE details")
            conn.commit()
            print("🗑️  ลบ table 'details' แล้ว")
        else:
            print("📝 เก็บ table 'details' ไว้ (สามารถลบทีหลังได้)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

def check_database_status():
    """ตรวจสอบสถานะของฐานข้อมูล"""
    db_path = os.path.join("backend", "dev.db")
    
    if not os.path.exists(db_path):
        print(f"❌ ไม่พบไฟล์ฐานข้อมูล: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 ตรวจสอบ tables ในฐานข้อมูล:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   - {table_name}: {count} records")
            
            # แสดงตัวอย่างข้อมูลจาก details และ credit
            if table_name in ['details', 'credit']:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                sample_records = cursor.fetchall()
                if sample_records:
                    print(f"     ตัวอย่างข้อมูล:")
                    for record in sample_records:
                        print(f"       {record}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error ตรวจสอบฐานข้อมูล: {e}")

if __name__ == "__main__":
    print("🚀 Migration Tool: details → credit")
    print("=" * 50)
    
    # ตรวจสอบสถานะฐานข้อมูลก่อน
    print("📊 สถานะฐานข้อมูลปัจจุบัน:")
    check_database_status()
    
    print("\n" + "=" * 50)
    response = input("คุณต้องการเริ่ม migration หรือไม่? (y/N): ")
    
    if response.lower() == 'y':
        success = migrate_details_to_credit()
        
        if success:
            print("\n✅ Migration เสร็จสิ้น!")
            print("💡 อย่าลืมทดสอบระบบให้แน่ใจว่าทุกอย่างทำงานปกติ")
        else:
            print("\n❌ Migration ล้มเหลว")
    else:
        print("❌ ยกเลิก migration")