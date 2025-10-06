#!/usr/bin/env python3
"""
Migration script: ย้ายข้อมูลจาก table 'details' ไปยัง table 'credit'
"""

import os
import sys
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
from datetime import datetime

# เพิ่ม path ของ backend app
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

# Import models
from backend.app.models import SessionLocal, Base, User, Credit

def migrate_details_to_credit():
    """ย้ายข้อมูลจาก details table ไปยัง credit table"""
    
    db = SessionLocal()
    
    try:
        # ตรวจสอบว่ามี table details อยู่หรือไม่
        engine = db.get_bind()
        inspector = engine.dialect.get_table_names(engine.connect())
        
        if 'details' not in inspector:
            print("❌ Table 'details' ไม่พบในฐานข้อมูล")
            return False
        
        print("🔍 ตรวจสอบข้อมูลใน table 'details'...")
        
        # ดึงข้อมูลจาก details table
        result = db.execute(text("SELECT * FROM details"))
        details_records = result.fetchall()
        
        if not details_records:
            print("📝 ไม่พบข้อมูลใน table 'details'")
            return True
        
        print(f"📊 พบข้อมูล {len(details_records)} records ใน table 'details'")
        
        # แสดงข้อมูลที่จะย้าย
        for record in details_records:
            print(f"   - user_id: {record.user_id}, balance: {record.balance}")
        
        # ตรวจสอบว่ามี credit table อยู่แล้วหรือไม่
        if 'credit' in inspector:
            print("⚠️  Table 'credit' มีอยู่แล้ว")
            
            # ตรวจสอบว่ามีข้อมูลใน credit หรือไม่
            credit_count = db.execute(text("SELECT COUNT(*) FROM credit")).scalar()
            if credit_count > 0:
                print(f"⚠️  Table 'credit' มีข้อมูล {credit_count} records อยู่แล้ว")
                response = input("คุณต้องการเขียนทับข้อมูลเดิมหรือไม่? (y/N): ")
                if response.lower() != 'y':
                    print("❌ ยกเลิกการ migrate")
                    return False
                
                # ลบข้อมูลเดิมใน credit table
                db.execute(text("DELETE FROM credit"))
                print("🗑️  ลบข้อมูลเดิมใน table 'credit' แล้ว")
        
        # สร้าง credit table หากยังไม่มี
        print("🔧 สร้าง table 'credit'...")
        Base.metadata.create_all(bind=engine)
        
        # ย้ายข้อมูลจาก details ไปยัง credit
        print("📦 เริ่มย้ายข้อมูล...")
        
        migrated_count = 0
        for record in details_records:
            try:
                # ตรวจสอบว่า user_id มีอยู่ใน users table หรือไม่
                user_exists = db.query(User).filter(User.id == record.user_id).first()
                if not user_exists:
                    print(f"⚠️  ข้าม user_id {record.user_id} (ไม่พบใน users table)")
                    continue
                
                # สร้าง Credit record ใหม่
                credit_record = Credit(
                    user_id=record.user_id,
                    balance=Decimal(str(record.balance)) if record.balance else Decimal('0.00'),
                    created_at=record.created_at if hasattr(record, 'created_at') else datetime.utcnow(),
                    updated_at=record.updated_at if hasattr(record, 'updated_at') else datetime.utcnow()
                )
                
                db.add(credit_record)
                migrated_count += 1
                print(f"✅ ย้ายข้อมูล user_id: {record.user_id}, balance: {record.balance}")
                
            except Exception as e:
                print(f"❌ Error ย้ายข้อมูล user_id {record.user_id}: {e}")
                continue
        
        # Commit การเปลี่ยนแปลง
        db.commit()
        print(f"🎉 Migration สำเร็จ! ย้ายข้อมูล {migrated_count}/{len(details_records)} records")
        
        # ตรวจสอบข้อมูลใน credit table
        print("\n🔍 ตรวจสอบข้อมูลใน table 'credit' หลัง migration:")
        credit_records = db.query(Credit).all()
        for credit in credit_records:
            print(f"   - user_id: {credit.user_id}, balance: {credit.balance}")
        
        # ถามว่าต้องการลบ details table หรือไม่
        print(f"\n📝 Table 'details' ยังคงมีอยู่ ({len(details_records)} records)")
        response = input("คุณต้องการลบ table 'details' หรือไม่? (y/N): ")
        if response.lower() == 'y':
            db.execute(text("DROP TABLE details"))
            db.commit()
            print("🗑️  ลบ table 'details' แล้ว")
        else:
            print("📝 เก็บ table 'details' ไว้ (สามารถลบทีหลังได้)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 เริ่ม Migration: details → credit")
    print("=" * 50)
    
    success = migrate_details_to_credit()
    
    if success:
        print("\n✅ Migration เสร็จสิ้น!")
        print("💡 อย่าลืมทดสอบระบบให้แน่ใจว่าทุกอย่างทำงานปกติ")
    else:
        print("\n❌ Migration ล้มเหลว")
        print("💡 กรุณาตรวจสอบ error และลองใหม่")