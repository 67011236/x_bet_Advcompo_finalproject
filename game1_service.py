"""
Game1 Service - จัดการข้อมูลการเล่นเกม 1
รวมถึงการบันทึกผลการเล่น อัพเดทยอดเงิน และสถิติการเล่น
"""

import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
import random

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/xbet_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class Game1Service:
    def __init__(self):
        self.session = SessionLocal()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def play_game(self, user_id: int, bet_amount: float, selected_color: str) -> Dict[str, Any]:
        """
        เล่นเกม 1 - วงล้อสี
        
        Args:
            user_id: ID ของผู้ใช้
            bet_amount: จำนวนเงินที่เดิมพัน
            selected_color: สีที่เลือก ('blue' หรือ 'white')
            
        Returns:
            Dict ที่มีผลลัพธ์การเล่นเกม
        """
        try:
            # ตรวจสอบยอดเงินของผู้ใช้
            balance_result = self.session.execute(
                text("SELECT balance FROM credit WHERE user_id = :user_id"),
                {"user_id": user_id}
            ).fetchone()
            
            if not balance_result:
                return {"success": False, "error": "ไม่พบข้อมูลยอดเงินของผู้ใช้"}
            
            current_balance = float(balance_result[0])
            
            if current_balance < bet_amount:
                return {"success": False, "error": "ยอดเงินไม่เพียงพอ"}
            
            # สุ่มผลลัพธ์ (50% โอกาสแต่ละสี)
            result_color = random.choice(['blue', 'white'])
            won = 1 if selected_color == result_color else 0
            
            # คำนวณจำนวนเงินที่ชนะ/แพ้
            if won:
                win_loss_amount = bet_amount  # ชนะได้เท่าที่เดิมพัน
                new_balance = current_balance + bet_amount
            else:
                win_loss_amount = -bet_amount  # แพ้เสียเท่าที่เดิมพัน
                new_balance = current_balance - bet_amount
            
            # อัพเดทยอดเงินในตาราง credit
            self.session.execute(
                text("UPDATE credit SET balance = :new_balance, updated_at = NOW() WHERE user_id = :user_id"),
                {"new_balance": new_balance, "user_id": user_id}
            )
            
            # บันทึกผลการเล่นในตาราง game1
            self.session.execute(
                text("""
                    INSERT INTO game1 (
                        user_id, bet_amount, selected_color, result_color, 
                        won, win_loss_amount, balance_before, balance_after, played_at
                    ) VALUES (
                        :user_id, :bet_amount, :selected_color, :result_color,
                        :won, :win_loss_amount, :balance_before, :balance_after, NOW()
                    )
                """),
                {
                    "user_id": user_id,
                    "bet_amount": bet_amount,
                    "selected_color": selected_color,
                    "result_color": result_color,
                    "won": won,
                    "win_loss_amount": win_loss_amount,
                    "balance_before": current_balance,
                    "balance_after": new_balance
                }
            )
            
            self.session.commit()
            
            return {
                "success": True,
                "result": {
                    "selected_color": selected_color,
                    "result_color": result_color,
                    "won": bool(won),
                    "bet_amount": bet_amount,
                    "win_loss_amount": win_loss_amount,
                    "balance_before": current_balance,
                    "balance_after": new_balance,
                    "message": "" if won else ""
                }
            }
            
        except Exception as e:
            self.session.rollback()
            return {"success": False, "error": f"เกิดข้อผิดพลาด: {str(e)}"}

    def get_user_game_history(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        ดึงประวัติการเล่นเกมของผู้ใช้
        
        Args:
            user_id: ID ของผู้ใช้
            limit: จำนวนรายการที่ต้องการ
            offset: จำนวนรายการที่ข้าม
            
        Returns:
            List ของประวัติการเล่นเกม
        """
        try:
            result = self.session.execute(
                text("""
                    SELECT id, bet_amount, selected_color, result_color, won, 
                           win_loss_amount, balance_before, balance_after, played_at
                    FROM game1 
                    WHERE user_id = :user_id 
                    ORDER BY played_at DESC 
                    LIMIT :limit OFFSET :offset
                """),
                {"user_id": user_id, "limit": limit, "offset": offset}
            ).fetchall()
            
            history = []
            for row in result:
                history.append({
                    "id": row[0],
                    "bet_amount": float(row[1]),
                    "selected_color": row[2],
                    "result_color": row[3],
                    "won": bool(row[4]),
                    "win_loss_amount": float(row[5]),
                    "balance_before": float(row[6]),
                    "balance_after": float(row[7]),
                    "played_at": row[8].isoformat() if row[8] else None
                })
            
            return history
            
        except Exception as e:
            print(f"Error fetching game history: {str(e)}")
            return []

    def get_user_game_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        ดึงสถิติการเล่นเกมของผู้ใช้
        
        Args:
            user_id: ID ของผู้ใช้
            
        Returns:
            Dict ของสถิติการเล่นเกม
        """
        try:
            result = self.session.execute(
                text("""
                    SELECT total_games_played, total_wins, total_losses,
                           total_bet_amount, total_win_amount, total_loss_amount,
                           net_profit_loss, win_percentage, first_played_at, last_played_at
                    FROM game1_stats 
                    WHERE user_id = :user_id
                """),
                {"user_id": user_id}
            ).fetchone()
            
            if not result:
                return {
                    "total_games_played": 0,
                    "total_wins": 0,
                    "total_losses": 0,
                    "total_bet_amount": 0.0,
                    "total_win_amount": 0.0,
                    "total_loss_amount": 0.0,
                    "net_profit_loss": 0.0,
                    "win_percentage": 0.0,
                    "first_played_at": None,
                    "last_played_at": None
                }
            
            return {
                "total_games_played": result[0],
                "total_wins": result[1],
                "total_losses": result[2],
                "total_bet_amount": float(result[3]),
                "total_win_amount": float(result[4]),
                "total_loss_amount": float(result[5]),
                "net_profit_loss": float(result[6]),
                "win_percentage": float(result[7]) if result[7] else 0.0,
                "first_played_at": result[8].isoformat() if result[8] else None,
                "last_played_at": result[9].isoformat() if result[9] else None
            }
            
        except Exception as e:
            print(f"Error fetching game stats: {str(e)}")
            return None

    def get_all_users_game_stats(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        ดึงสถิติการเล่นเกมของผู้ใช้ทุกคน (สำหรับ Admin)
        
        Args:
            limit: จำนวนรายการที่ต้องการ
            
        Returns:
            List ของสถิติการเล่นเกมทุกคน
        """
        try:
            result = self.session.execute(
                text("""
                    SELECT gs.user_id, u.full_name, u.email,
                           gs.total_games_played, gs.total_wins, gs.total_losses,
                           gs.total_bet_amount, gs.net_profit_loss, gs.win_percentage,
                           gs.last_played_at
                    FROM game1_stats gs
                    JOIN users u ON gs.user_id = u.id
                    ORDER BY gs.total_games_played DESC, gs.net_profit_loss DESC
                    LIMIT :limit
                """),
                {"limit": limit}
            ).fetchall()
            
            stats_list = []
            for row in result:
                stats_list.append({
                    "user_id": row[0],
                    "full_name": row[1],
                    "email": row[2],
                    "total_games_played": row[3],
                    "total_wins": row[4],
                    "total_losses": row[5],
                    "total_bet_amount": float(row[6]),
                    "net_profit_loss": float(row[7]),
                    "win_percentage": float(row[8]) if row[8] else 0.0,
                    "last_played_at": row[9].isoformat() if row[9] else None
                })
            
            return stats_list
            
        except Exception as e:
            print(f"Error fetching all users game stats: {str(e)}")
            return []

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    # สร้างตารางก่อน (ใช้ไฟล์ SQL ที่สร้างไว้)
    print("ตัวอย่างการใช้งาน Game1Service:")
    
    with Game1Service() as game_service:
        # เล่นเกม
        user_id = 1
        result = game_service.play_game(user_id, 100.0, "blue")
        print(f"ผลการเล่นเกม: {result}")
        
        # ดูสถิติ
        stats = game_service.get_user_game_stats(user_id)
        print(f"สถิติการเล่น: {stats}")
        
        # ดูประวัติ
        history = game_service.get_user_game_history(user_id, limit=5)
        print(f"ประวัติ 5 ครั้งล่าสุด: {history}")