#!/usr/bin/env python3
"""
Script สำหรับตรวจสอบและสร้าง table 'reports' ในฐานข้อมูล
"""

import sqlite3
import os
from datetime import datetime

def create_reports_table():
    """สร้าง table 'reports' ในฐานข้อมูล"""
    
    # เชื่อมต่อฐานข้อมูล
    db_path = os.path.join("backend", "dev.db")
    
    if not os.path.exists(db_path):
        print(f"❌ ไม่พบไฟล์ฐานข้อมูล: {db_path}")
        print("💡 กรุณารัน backend server ก่อนเพื่อสร้างฐานข้อมูล")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 ตรวจสอบ tables ที่มีอยู่...")
        
        # ตรวจสอบว่ามี table reports อยู่หรือไม่
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reports'")
        reports_exists = cursor.fetchone()
        
        if reports_exists:
            print("✅ Table 'reports' มีอยู่แล้ว")
            
            # แสดงโครงสร้าง table
            cursor.execute("PRAGMA table_info(reports)")
            columns = cursor.fetchall()
            print("\n📋 โครงสร้าง table 'reports':")
            for col in columns:
                print(f"   - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
            
            # แสดงจำนวน records
            cursor.execute("SELECT COUNT(*) as count FROM reports")
            count = cursor.fetchone()[0]
            print(f"\n📊 จำนวน reports: {count} records")
            
            if count > 0:
                cursor.execute("SELECT id, title, category, status, created_at FROM reports ORDER BY created_at DESC LIMIT 5")
                recent_reports = cursor.fetchall()
                print("\n📝 Reports ล่าสุด (5 รายการ):")
                for report in recent_reports:
                    print(f"   - [{report[0]}] {report[1][:30]}... ({report[2]}) - {report[3]}")
        else:
            print("❌ ไม่พบ table 'reports'")
            print("🔧 กำลังสร้าง table 'reports'...")
            
            # สร้าง table reports
            create_table_sql = """
            CREATE TABLE reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title VARCHAR(255) NOT NULL,
                category VARCHAR(50) NOT NULL,
                description TEXT NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                CHECK (category IN ('technical','payment','account','betting','suggestion','other')),
                CHECK (status IN ('pending','reviewing','resolved','closed'))
            )
            """
            
            cursor.execute(create_table_sql)
            conn.commit()
            print("✅ สร้าง table 'reports' สำเร็จ!")
        
        # แสดง tables ทั้งหมด
        print("\n🗃️  Tables ทั้งหมดในฐานข้อมูล:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
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

def test_report_creation():
    """ทดสอบการสร้าง report"""
    db_path = os.path.join("backend", "dev.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ตรวจสอบว่ามี user อยู่หรือไม่
        cursor.execute("SELECT id, email FROM users LIMIT 1")
        user = cursor.fetchone()
        
        if not user:
            print("❌ ไม่พบ user ในฐานข้อมูล")
            return False
        
        print(f"👤 พบ user: {user[1]} (ID: {user[0]})")
        
        # สร้าง test report
        test_report = {
            'user_id': user[0],
            'title': 'Test Report - System Check',
            'category': 'technical',
            'description': 'This is a test report to verify the reports system is working correctly.',
            'status': 'pending'
        }
        
        cursor.execute("""
            INSERT INTO reports (user_id, title, category, description, status)
            VALUES (?, ?, ?, ?, ?)
        """, (test_report['user_id'], test_report['title'], test_report['category'], 
              test_report['description'], test_report['status']))
        
        conn.commit()
        
        # ดึง report ที่เพิ่งสร้าง
        report_id = cursor.lastrowid
        print(f"✅ สร้าง test report สำเร็จ (ID: {report_id})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test report: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 Reports Table Setup Tool")
    print("=" * 50)
    
    success = create_reports_table()
    
    if success:
        print("\n" + "=" * 50)
        response = input("คุณต้องการสร้าง test report หรือไม่? (y/N): ")
        if response.lower() == 'y':
            test_success = test_report_creation()
            if test_success:
                print("🎉 ระบบ reports พร้อมใช้งานแล้ว!")
            else:
                print("⚠️  ระบบ reports สร้างเสร็จแล้ว แต่การทดสอบล้มเหลว")
        else:
            print("✅ ระบบ reports พร้อมใช้งานแล้ว!")
    else:
        print("\n❌ การสร้าง table reports ล้มเหลว")