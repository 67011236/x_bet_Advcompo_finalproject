"""
สคริปต์ทดสอบ Game1 API ใหม่ที่ใช้ตาราง game1 เดียว
"""

import requests
import json

def test_game1_api():
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    print("🚀 ทดสอบ Game1 API")
    print("=" * 40)
    
    # 1. Login
    login_data = {
        "email": "test2@gmail.com", 
        "password": "123456"
    }
    
    print("1. กำลัง Login...")
    response = session.post(f"{base_url}/login", json=login_data)
    if response.status_code == 200:
        print("✅ Login สำเร็จ")
    else:
        print(f"❌ Login ล้มเหลว: {response.status_code}")
        return
    
    # 2. ตรวจสอบยอดเงิน
    print("\n2. ตรวจสอบยอดเงิน...")
    response = session.get(f"{base_url}/balance")
    if response.status_code == 200:
        balance = response.json().get("balance", 0)
        print(f"💰 ยอดเงินปัจจุบัน: {balance} บาท")
    
    # 3. เล่นเกม
    print("\n3. กำลังเล่น Game1...")
    game_data = {
        "bet_amount": 50.0,
        "selected_color": "blue"
    }
    
    response = session.post(f"{base_url}/api/game1/play", json=game_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            game_result = result["result"]
            print(f"🎮 ผลเกม: {game_result['selected_color']} vs {game_result['result_color']}")
            print(f"{'🎉 ชนะ' if game_result['won'] else '😢 แพ้'}: {game_result['win_loss_amount']} บาท")
        else:
            print(f"❌ เล่นเกมล้มเหลว: {result}")
    else:
        print(f"❌ API Error: {response.status_code}")
    
    # 4. ดูสถิติ
    print("\n4. ดูสถิติการเล่น...")
    response = session.get(f"{base_url}/api/game1/stats")
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            stats = data["stats"]
            print(f"📊 สถิติ:")
            print(f"   - เล่นทั้งหมด: {stats['total_games']} เกม")
            print(f"   - ชนะ: {stats['total_wins']} ครั้ง ({stats['win_percentage']}%)")
            print(f"   - กำไร/ขาดทุน: {stats['net_profit_loss']} บาท")

if __name__ == "__main__":
    test_game1_api()