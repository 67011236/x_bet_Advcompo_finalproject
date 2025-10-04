import sqlite3

# เชื่อมต่อ SQLite database
conn = sqlite3.connect('backend/dev.db')
cursor = conn.cursor()

print("=== SQLite Database Info ===")

# ดู tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"Tables: {tables}")

if tables:
    # ดูจำนวน users
    cursor.execute("SELECT COUNT(*) FROM users;")
    user_count = cursor.fetchone()[0]
    print(f"Total users: {user_count}")
    
    # ดูรายชื่อ users
    cursor.execute("SELECT id, email, full_name, role FROM users;")
    users = cursor.fetchall()
    print(f"\nUsers list:")
    for user in users:
        print(f"  ID: {user[0]}, Email: {user[1]}, Name: {user[2]}, Role: {user[3]}")

conn.close()