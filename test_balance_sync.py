"""
Test script สำหรับทดสอบ Balance sync ระหว่าง Frontend และ Database
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_balance_sync():
    """ทดสอบการ sync balance ระหว่าง frontend และ database"""
    
    # 1. Login
    print("1. 🔐 Logging in...")
    login_response = requests.post(f"{API_BASE}/login", 
        json={"email": "testbalance@gmail.com", "password": "123456"},
        cookies={}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return False
    
    # เก็บ cookies
    cookies = login_response.cookies
    print("✅ Login successful")
    
    # 2. ตรวจสอบ balance เริ่มต้น
    print("\n2. 💰 Checking initial balance...")
    balance_response = requests.get(f"{API_BASE}/balance", cookies=cookies)
    
    if balance_response.status_code != 200:
        print(f"❌ Failed to get balance: {balance_response.text}")
        return False
    
    initial_balance_data = balance_response.json()
    initial_balance = initial_balance_data["amount"]
    print(f"💰 Initial balance: {initial_balance} THB")
    print(f"👤 User ID: {initial_balance_data['user_id']}")
    
    # 3. เติมเงินถ้ายอดไม่พอ
    if initial_balance < 500:
        print(f"\n3. 💸 Balance too low, depositing 1000 THB...")
        deposit_response = requests.post(f"{API_BASE}/deposit",
            json={"amount": 1000},
            cookies=cookies
        )
        
        if deposit_response.status_code == 200:
            print("✅ Deposit successful")
            
            # ตรวจสอบ balance หลัง deposit
            balance_response = requests.get(f"{API_BASE}/balance", cookies=cookies)
            new_balance_data = balance_response.json()
            new_balance = new_balance_data["amount"]
            print(f"💰 Balance after deposit: {new_balance} THB")
            initial_balance = new_balance
        else:
            print(f"❌ Deposit failed: {deposit_response.text}")
            return False
    
    # 4. เล่นเกม 1 ครั้ง
    print(f"\n4. 🎮 Playing Game1...")
    bet_amount = 100
    selected_color = "blue"
    
    game_response = requests.post(f"{API_BASE}/api/game1/play",
        json={"bet_amount": bet_amount, "selected_color": selected_color},
        cookies=cookies
    )
    
    if game_response.status_code != 200:
        print(f"❌ Game play failed: {game_response.text}")
        return False
    
    game_result = game_response.json()
    if not game_result.get("success"):
        print(f"❌ Game API returned error: {game_result}")
        return False
    
    result = game_result["result"]
    won = result["won"]
    win_loss_amount = result["win_loss_amount"]
    api_balance_after = result["balance_after"]
    
    print(f"🎲 Game result: {selected_color} → {result['result_color']}")
    print(f"{'🎉 WON' if won else '💔 LOST'}: {win_loss_amount} THB")
    print(f"📊 API says balance: {result['balance_before']} → {api_balance_after}")
    
    # 5. ตรวจสอบ balance จาก API อีกครั้ง
    print(f"\n5. 🔄 Verifying balance from database...")
    time.sleep(1)  # รอให้ database update เสร็จ
    
    balance_response = requests.get(f"{API_BASE}/balance", cookies=cookies)
    if balance_response.status_code != 200:
        print(f"❌ Failed to get balance: {balance_response.text}")
        return False
    
    final_balance_data = balance_response.json()
    db_balance = final_balance_data["amount"]
    
    print(f"💰 Database balance: {db_balance} THB")
    print(f"💰 API response balance: {api_balance_after} THB")
    
    # 6. เปรียบเทียบผลลัพธ์
    print(f"\n6. 📋 Balance Comparison:")
    expected_balance = initial_balance + win_loss_amount
    
    print(f"   Initial balance: {initial_balance}")
    print(f"   Win/Loss amount: {win_loss_amount}")
    print(f"   Expected balance: {expected_balance}")
    print(f"   API balance: {api_balance_after}")
    print(f"   DB balance: {db_balance}")
    
    # ตรวจสอบความถูกต้อง
    api_correct = abs(api_balance_after - expected_balance) < 0.01
    db_correct = abs(db_balance - expected_balance) < 0.01
    sync_correct = abs(api_balance_after - db_balance) < 0.01
    
    print(f"\n7. ✅ Verification Results:")
    print(f"   API calculation correct: {'✅' if api_correct else '❌'}")
    print(f"   DB update correct: {'✅' if db_correct else '❌'}")
    print(f"   API-DB sync correct: {'✅' if sync_correct else '❌'}")
    
    if api_correct and db_correct and sync_correct:
        print(f"\n🎉 ALL TESTS PASSED! Balance sync is working correctly.")
        return True
    else:
        print(f"\n💥 TESTS FAILED! Balance sync has issues.")
        return False

def test_multiple_games():
    """ทดสอบการเล่นหลายเกมติดกัน"""
    
    print("\n" + "="*50)
    print("🔄 Testing Multiple Games...")
    
    # Login
    login_response = requests.post(f"{API_BASE}/login", 
        json={"email": "testbalance@gmail.com", "password": "123456"}
    )
    cookies = login_response.cookies
    
    # เล่น 5 เกม
    for i in range(1, 6):
        print(f"\n🎮 Game {i}/5:")
        
        # ดู balance ก่อนเล่น
        balance_before = requests.get(f"{API_BASE}/balance", cookies=cookies).json()["amount"]
        
        # เล่นเกม
        game_response = requests.post(f"{API_BASE}/api/game1/play",
            json={"bet_amount": 50, "selected_color": "blue" if i % 2 == 0 else "white"},
            cookies=cookies
        )
        
        if game_response.status_code == 200:
            result = game_response.json()["result"]
            
            # ดู balance หลังเล่น
            time.sleep(0.5)
            balance_after = requests.get(f"{API_BASE}/balance", cookies=cookies).json()["amount"]
            
            print(f"   Balance: {balance_before} → {balance_after} (API: {result['balance_after']})")
            print(f"   Result: {'WON' if result['won'] else 'LOST'} {result['win_loss_amount']}")
            
            # ตรวจสอบ sync
            if abs(balance_after - result['balance_after']) < 0.01:
                print(f"   ✅ Sync correct")
            else:
                print(f"   ❌ Sync error: DB={balance_after}, API={result['balance_after']}")
        else:
            print(f"   ❌ Game failed: {game_response.text}")

if __name__ == "__main__":
    print("🧪 Balance Sync Test Suite")
    print("=" * 50)
    
    # ทดสอบเกมเดียว
    success = test_balance_sync()
    
    if success:
        # ทดสอบหลายเกม
        test_multiple_games()
    
    print("\n🏁 Test completed!")