"""
ไฟล์สำหรับทดสอบระบบ Game1 
รวมการทดสอบ API, Database และ Business Logic
"""

import requests
import json
import time
import random
from datetime import datetime

class Game1Tester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_email = "test@gmail.com"
        self.test_password = "123456"

    def login(self):
        """เข้าสู่ระบบ"""
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = self.session.post(f"{self.base_url}/login", json=login_data)
        if response.status_code == 200:
            print(f"✅ Login successful: {self.test_email}")
            return True
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False

    def check_balance(self):
        """ตรวจสอบยอดเงิน"""
        response = self.session.get(f"{self.base_url}/balance")
        if response.status_code == 200:
            data = response.json()
            balance = data.get("balance", 0)
            print(f"💰 Current balance: {balance} บาท")
            return balance
        else:
            print(f"❌ Failed to get balance: {response.status_code}")
            return 0

    def deposit_money(self, amount=1000):
        """เติมเงิน"""
        deposit_data = {"amount": amount}
        response = self.session.post(f"{self.base_url}/deposit", json=deposit_data)
        if response.status_code == 200:
            print(f"✅ Deposited {amount} บาท")
            return True
        else:
            print(f"❌ Deposit failed: {response.status_code} - {response.text}")
            return False

    def play_game1(self, bet_amount, selected_color):
        """เล่น Game1"""
        game_data = {
            "bet_amount": bet_amount,
            "selected_color": selected_color
        }
        
        response = self.session.post(f"{self.base_url}/api/game1/play", json=game_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                game_result = result["result"]
                won = game_result["won"]
                print(f"🎮 Game result: {selected_color} vs {game_result['result_color']} - {'WON' if won else 'LOST'} {game_result['win_loss_amount']} บาท")
                return result
            else:
                print(f"❌ Game play failed: {result}")
                return None
        else:
            print(f"❌ API call failed: {response.status_code} - {response.text}")
            return None

    def get_game_stats(self):
        """ดูสถิติการเล่น"""
        response = self.session.get(f"{self.base_url}/api/game1/stats")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                stats = data["stats"]
                print(f"📊 Game Stats:")
                print(f"   - Total Games: {stats['total_games']}")
                print(f"   - Wins: {stats['total_wins']} ({stats['win_percentage']}%)")
                print(f"   - Losses: {stats['total_losses']}")
                print(f"   - Total Bet: {stats['total_bet_amount']} บาท")
                print(f"   - Net P&L: {stats['net_profit_loss']} บาท")
                return stats
            else:
                print(f"❌ Failed to get stats: {data}")
                return None
        else:
            print(f"❌ API call failed: {response.status_code}")
            return None

    def get_game_history(self, limit=5):
        """ดูประวัติการเล่น"""
        response = self.session.get(f"{self.base_url}/api/game1/history?limit={limit}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                history = data["history"]
                print(f"📜 Recent {len(history)} games:")
                for i, game in enumerate(history, 1):
                    won_text = "WON" if game["won"] else "LOST"
                    print(f"   {i}. {game['selected_color']} vs {game['result_color']} - {won_text} {game['win_loss_amount']} บาท")
                return history
            else:
                print(f"❌ Failed to get history: {data}")
                return None
        else:
            print(f"❌ API call failed: {response.status_code}")
            return None

    def run_basic_test(self):
        """รันการทดสอบพื้นฐาน"""
        print("🚀 Starting Game1 Basic Test")
        print("=" * 50)
        
        # 1. เข้าสู่ระบบ
        if not self.login():
            print("❌ Cannot proceed without login")
            return False
        
        # 2. ตรวจสอบยอดเงิน
        initial_balance = self.check_balance()
        
        # 3. เติมเงินถ้ายอดไม่พอ
        if initial_balance < 500:
            print("💸 Balance too low, depositing money...")
            self.deposit_money(1000)
            initial_balance = self.check_balance()
        
        # 4. เล่นเกมหลายครั้ง
        colors = ["blue", "white"]
        bet_amounts = [50, 100, 200]
        
        print(f"\n🎮 Playing 5 games...")
        for i in range(5):
            bet_amount = random.choice(bet_amounts)
            selected_color = random.choice(colors)
            
            print(f"\n--- Game {i+1} ---")
            result = self.play_game1(bet_amount, selected_color)
            
            if result:
                time.sleep(0.5)  # รอหน่อยระหว่างเกม
        
        # 5. ดูสถิติ
        print(f"\n📊 Final Statistics:")
        print("-" * 30)
        self.get_game_stats()
        
        # 6. ดูประวัติ
        print(f"\n📜 Game History:")
        print("-" * 30)
        self.get_game_history()
        
        # 7. ดูยอดเงินสุดท้าย
        final_balance = self.check_balance()
        profit_loss = final_balance - initial_balance
        print(f"\n💹 Balance Change: {profit_loss:+.2f} บาท")
        
        print(f"\n✅ Basic test completed!")
        return True

    def run_stress_test(self, num_games=50):
        """รันการทดสอบความเร็ว"""
        print(f"🔥 Starting Game1 Stress Test ({num_games} games)")
        print("=" * 50)
        
        if not self.login():
            return False
        
        initial_balance = self.check_balance()
        if initial_balance < num_games * 100:
            self.deposit_money(num_games * 100)
        
        results = []
        start_time = time.time()
        
        for i in range(num_games):
            if i % 10 == 0:
                print(f"Progress: {i}/{num_games}")
            
            result = self.play_game1(100, random.choice(["blue", "white"]))
            if result:
                results.append(result)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n📊 Stress Test Results:")
        print(f"   - Games played: {len(results)}")
        print(f"   - Duration: {duration:.2f} seconds")
        print(f"   - Games per second: {len(results)/duration:.2f}")
        
        # ดูสถิติสุดท้าย
        self.get_game_stats()
        
        final_balance = self.check_balance()
        profit_loss = final_balance - initial_balance
        print(f"   - Total P&L: {profit_loss:+.2f} บาท")
        
        return True

    def run_edge_case_test(self):
        """ทดสอบกรณีพิเศษ"""
        print("🧪 Starting Edge Case Test")
        print("=" * 50)
        
        if not self.login():
            return False
        
        # 1. ทดสอบเดิมพันจำนวนน้อย
        print("Testing small bet...")
        self.play_game1(1, "blue")
        
        # 2. ทดสอบเดิมพันจำนวนมาก (ถ้ายอดพอ)
        balance = self.check_balance()
        if balance >= 1000:
            print("Testing large bet...")
            self.play_game1(1000, "white")
        
        # 3. ทดสอบเดิมพันเกินยอด
        print("Testing insufficient balance...")
        try:
            result = self.play_game1(999999, "blue")
            if result and not result.get("success"):
                print("✅ Correctly rejected insufficient balance")
        except:
            print("✅ API correctly handled insufficient balance")
        
        # 4. ทดสอบสีผิด
        print("Testing invalid color...")
        invalid_data = {
            "bet_amount": 100,
            "selected_color": "red"  # สีไม่ถูกต้อง
        }
        response = self.session.post(f"{self.base_url}/api/game1/play", json=invalid_data)
        if response.status_code == 400:
            print("✅ Correctly rejected invalid color")
        
        return True

def main():
    """ฟังก์ชันหลักสำหรับรันการทดสอบ"""
    tester = Game1Tester()
    
    print("🎯 Game1 Testing Suite")
    print("=" * 50)
    
    while True:
        print("\nSelect test to run:")
        print("1. Basic Test (5 games)")
        print("2. Stress Test (50 games)")
        print("3. Edge Case Test")
        print("4. All Tests")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-4): ")
        
        if choice == "1":
            tester.run_basic_test()
        elif choice == "2":
            tester.run_stress_test()
        elif choice == "3":
            tester.run_edge_case_test()
        elif choice == "4":
            tester.run_basic_test()
            print("\n" + "="*50)
            tester.run_stress_test()
            print("\n" + "="*50)
            tester.run_edge_case_test()
        elif choice == "0":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice, please try again")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    main()