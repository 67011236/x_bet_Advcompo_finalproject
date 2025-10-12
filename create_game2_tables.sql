-- SQL script to create Game2 tables for Rock Paper Scissors
-- Run this in DBeaver or your database management tool

-- ===============================
-- Game2 Table (เก็บข้อมูลการเล่นแต่ละครั้ง)
-- ===============================
CREATE TABLE IF NOT EXISTS game2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bet_amount DECIMAL(10,2) NOT NULL CHECK (bet_amount > 0),
    player_choice VARCHAR(10) NOT NULL CHECK (player_choice IN ('rock','paper','scissors')),
    bot_choice VARCHAR(10) NOT NULL CHECK (bot_choice IN ('rock','paper','scissors')),
    result VARCHAR(10) NOT NULL CHECK (result IN ('win','lose','tie')),
    win_loss_amount DECIMAL(10,2) NOT NULL,
    balance_before DECIMAL(10,2) NOT NULL,
    balance_after DECIMAL(10,2) NOT NULL,
    played_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ===============================
-- Game2 Statistics Table (เก็บสถิติรวมของแต่ละ user)
-- ===============================
CREATE TABLE IF NOT EXISTS game2_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    total_games_played INTEGER NOT NULL DEFAULT 0,
    total_wins INTEGER NOT NULL DEFAULT 0,
    total_losses INTEGER NOT NULL DEFAULT 0,
    total_ties INTEGER NOT NULL DEFAULT 0,
    total_bet_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total_win_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total_loss_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    net_profit_loss DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    rock_played INTEGER NOT NULL DEFAULT 0,
    paper_played INTEGER NOT NULL DEFAULT 0,
    scissors_played INTEGER NOT NULL DEFAULT 0,
    first_played_at DATETIME,
    last_played_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ===============================
-- Create Indexes for better performance
-- ===============================
CREATE INDEX IF NOT EXISTS idx_game2_user_id ON game2(user_id);
CREATE INDEX IF NOT EXISTS idx_game2_played_at ON game2(played_at);
CREATE INDEX IF NOT EXISTS idx_game2_result ON game2(result);

CREATE INDEX IF NOT EXISTS idx_game2_stats_user_id ON game2_stats(user_id);

-- ===============================
-- Sample Queries to check data
-- ===============================

-- ดูข้อมูลการเล่นล่าสุด 10 รอบ
-- SELECT 
--     g.id,
--     u.full_name,
--     u.email,
--     g.bet_amount,
--     g.player_choice,
--     g.bot_choice,
--     g.result,
--     g.win_loss_amount,
--     g.balance_after,
--     g.played_at
-- FROM game2 g
-- JOIN users u ON g.user_id = u.id
-- ORDER BY g.played_at DESC
-- LIMIT 10;

-- ดูสถิติของ user ทั้งหมด
-- SELECT 
--     u.full_name,
--     u.email,
--     s.total_games_played,
--     s.total_wins,
--     s.total_losses,
--     s.total_ties,
--     ROUND((s.total_wins * 100.0 / s.total_games_played), 2) as win_percentage,
--     s.net_profit_loss,
--     s.rock_played,
--     s.paper_played,
--     s.scissors_played
-- FROM game2_stats s
-- JOIN users u ON s.user_id = u.id
-- ORDER BY s.total_games_played DESC;

-- ดูการเล่นของ user คนใดคนหนึ่ง (แทนที่ USER_ID ด้วยตัวเลขที่ต้องการ)
-- SELECT 
--     bet_amount,
--     player_choice,
--     bot_choice,
--     result,
--     win_loss_amount,
--     balance_before,
--     balance_after,
--     played_at
-- FROM game2 
-- WHERE user_id = 1  -- เปลี่ยนเป็น user_id ที่ต้องการดู
-- ORDER BY played_at DESC
-- LIMIT 20;