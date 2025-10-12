#!/usr/bin/env python3
"""
Test Dashboard API - ทดสอบว่า API game-stats ทำงานได้หรือไม่
"""

import requests
import json
import time

def test_dashboard_api():
    """ทดสอบ API dashboard"""
    
    print("🧪 Testing Dashboard APIs...")
    
    base_url = "http://localhost:8000"
    
    # Test 1: Dashboard Stats
    try:
        print("\n📊 Testing /api/dashboard-stats...")
        response = requests.get(f"{base_url}/api/dashboard-stats")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard Stats: {data}")
        else:
            print(f"❌ Dashboard Stats failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Dashboard Stats error: {e}")
    
    # Test 2: Game Stats
    try:
        print("\n🎮 Testing /api/game-stats...")
        response = requests.get(f"{base_url}/api/game-stats")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Game Stats: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Game Stats failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Game Stats error: {e}")

def check_database_data():
    """ตรวจสอบข้อมูลใน database"""
    import sqlite3
    
    print("\n📂 Checking database data...")
    
    try:
        conn = sqlite3.connect("dev.db")
        cursor = conn.cursor()
        
        # ตรวจสอบ Game1 data
        cursor.execute("SELECT COUNT(*) FROM game1")
        game1_count = cursor.fetchone()[0]
        print(f"🎰 Game1 records: {game1_count}")
        
        # ตรวจสอบ Game2 data
        cursor.execute("SELECT COUNT(*) FROM game2")
        game2_count = cursor.fetchone()[0]
        print(f"🎮 Game2 records: {game2_count}")
        
        # ตรวจสอบ Users
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        print(f"👥 Users: {users_count}")
        
        # ดูข้อมูลล่าสุด Game1
        if game1_count > 0:
            cursor.execute("""
                SELECT u.email, g.bet_amount, g.selected_color, g.result_color, g.won, g.played_at 
                FROM game1 g 
                JOIN users u ON g.user_id = u.id 
                ORDER BY g.played_at DESC 
                LIMIT 3
            """)
            recent_game1 = cursor.fetchall()
            print(f"\n📊 Recent Game1 plays:")
            for play in recent_game1:
                print(f"   • {play[0]} bet {play[1]} on {play[2]} (result: {play[3]}, {'won' if play[4] else 'lost'}) at {play[5]}")
        
        # ดูข้อมูลล่าสุด Game2
        if game2_count > 0:
            cursor.execute("""
                SELECT u.email, g.bet_amount, g.player_choice, g.bot_choice, g.result, g.played_at 
                FROM game2 g 
                JOIN users u ON g.user_id = u.id 
                ORDER BY g.played_at DESC 
                LIMIT 3
            """)
            recent_game2 = cursor.fetchall()
            print(f"\n🎮 Recent Game2 plays:")
            for play in recent_game2:
                print(f"   • {play[0]} bet {play[1]} - {play[2]} vs {play[3]} = {play[4]} at {play[5]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

def simulate_dashboard_update():
    """จำลองการอัพเดท dashboard แบบ real-time"""
    
    print("\n🔄 Simulating real-time dashboard updates...")
    
    for i in range(3):
        print(f"\n--- Update {i+1} ---")
        check_database_data()
        time.sleep(2)

if __name__ == "__main__":
    print("🎯 Dashboard API Tester")
    print("=" * 50)
    
    # ตรวจสอบข้อมูลใน database ก่อน
    check_database_data()
    
    # ทดสอบ API (ถ้า server รันอยู่)
    print("\n" + "=" * 50)
    test_dashboard_api()
    
    # จำลอง real-time updates
    print("\n" + "=" * 50)
    simulate_dashboard_update()
    
    print("\n✅ Testing completed!")