#!/usr/bin/env python3
"""
Migration script: SQLite -> PostgreSQL
ย้ายข้อมูล users และ reports จาก SQLite ไป PostgreSQL
"""

import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
from datetime import datetime

def connect_sqlite():
    """เชื่อมต่อ SQLite database"""
    return sqlite3.connect('backend/dev.db')

def connect_postgres():
    """เชื่อมต่อ PostgreSQL database"""
    return psycopg2.connect(
        host='localhost',
        port=5432,
        database='xbet_db',
        user='postgres',
        password='postgres123'
    )

def create_tables_postgres(pg_conn):
    """สร้างตารางใน PostgreSQL"""
    with pg_conn.cursor() as cursor:
        # สร้างตาราง users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                age INTEGER NOT NULL,
                phone VARCHAR(20) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK (age >= 18 AND age <= 100),
                CHECK (phone ~ '^[0-9]{10}$')
            );
        """)
        
        # สร้างตาราง credit
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS credit (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                balance NUMERIC(15, 2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK (balance >= 0)
            );
        """)
        
        # สร้างตาราง reports
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                category VARCHAR(50) NOT NULL,
                description TEXT NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK (category IN ('technical','payment','account','betting','suggestion','other')),
                CHECK (status IN ('pending','in_progress','resolved','closed'))
            );
        """)
        
        pg_conn.commit()
        print("✅ สร้างตารางใน PostgreSQL เรียบร้อย")

def migrate_users(sqlite_conn, pg_conn):
    """ย้ายข้อมูล users"""
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("SELECT * FROM users")
    users = sqlite_cursor.fetchall()
    
    with pg_conn.cursor() as pg_cursor:
        for user in users:
            try:
                # ข้อมูลจาก SQLite: (id, full_name, age, phone, email, password_hash, role, created_at)
                user_id, full_name, age, phone, email, password_hash, role, created_at = user
                
                pg_cursor.execute("""
                    INSERT INTO users (id, full_name, age, phone, email, password_hash, role, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (email) DO UPDATE SET
                    full_name = EXCLUDED.full_name,
                    age = EXCLUDED.age,
                    phone = EXCLUDED.phone,
                    password_hash = EXCLUDED.password_hash,
                    role = EXCLUDED.role
                """, (user_id, full_name, age, phone, email, password_hash, role, created_at))
                print(f"✅ User: {email} (ID: {user_id}) - Role: {role}")
            except Exception as e:
                print(f"❌ Error migrating user {user[4]}: {e}")
        
        pg_conn.commit()
        print(f"✅ ย้าย {len(users)} users เรียบร้อย")

def migrate_credit(sqlite_conn, pg_conn):
    """ย้ายข้อมูล credit"""
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("SELECT * FROM credit")
    credits = sqlite_cursor.fetchall()
    
    with pg_conn.cursor() as pg_cursor:
        for credit in credits:
            try:
                pg_cursor.execute("""
                    INSERT INTO credit (id, user_id, balance, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, credit)
                print(f"✅ Credit: User ID {credit[1]} - Balance: {credit[2]}")
            except Exception as e:
                print(f"❌ Error migrating credit for user {credit[1]}: {e}")
        
        pg_conn.commit()
        print(f"✅ ย้าย {len(credits)} credit records เรียบร้อย")

def migrate_reports(sqlite_conn, pg_conn):
    """ย้ายข้อมูล reports"""
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("SELECT * FROM reports")
    reports = sqlite_cursor.fetchall()
    
    with pg_conn.cursor() as pg_cursor:
        for report in reports:
            try:
                pg_cursor.execute("""
                    INSERT INTO reports (id, user_id, title, category, description, status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, report)
                print(f"✅ Report: {report[2]} (User ID: {report[1]})")
            except Exception as e:
                print(f"❌ Error migrating report {report[2]}: {e}")
        
        pg_conn.commit()
        print(f"✅ ย้าย {len(reports)} reports เรียบร้อย")

def main():
    """Main migration function"""
    print("🚀 เริ่มการ migrate ข้อมูลจาก SQLite ไป PostgreSQL...")
    
    try:
        # เชื่อมต่อ databases
        sqlite_conn = connect_sqlite()
        pg_conn = connect_postgres()
        
        print("✅ เชื่อมต่อ databases สำเร็จ")
        
        # สร้างตาราง
        create_tables_postgres(pg_conn)
        
        # ย้ายข้อมูล
        migrate_users(sqlite_conn, pg_conn)
        migrate_credit(sqlite_conn, pg_conn)
        migrate_reports(sqlite_conn, pg_conn)
        
        print("🎉 Migration เสร็จสิ้น!")
        
    except sqlite3.Error as e:
        print(f"❌ SQLite Error: {e}")
        sys.exit(1)
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)
    finally:
        if 'sqlite_conn' in locals():
            sqlite_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    main()