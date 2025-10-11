-- สร้างตาราง game1 สำหรับเก็บข้อมูลการเล่นเกมและสถิติของผู้ใช้แต่ละคน
CREATE TABLE IF NOT EXISTS game1 (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- ข้อมูลการเล่นครั้งล่าสุด
    bet_amount NUMERIC(10, 2) NOT NULL CHECK (bet_amount > 0),
    selected_color VARCHAR(10) NOT NULL CHECK (selected_color IN ('blue', 'white')),
    result_color VARCHAR(10) NOT NULL CHECK (result_color IN ('blue', 'white')),
    won INTEGER NOT NULL CHECK (won IN (0, 1)),
    win_loss_amount NUMERIC(10, 2) NOT NULL,  -- จำนวนที่ชนะ/แพ้ (+100 ชนะ, -100 แพ้)
    balance_before NUMERIC(10, 2) NOT NULL,   -- ยอดเงินก่อนเล่น
    balance_after NUMERIC(10, 2) NOT NULL,    -- ยอดเงินหลังเล่น
    
    -- สถิติการเล่นรวมของผู้ใช้ (ต่อ 1 user มี 1 row ล่าสุดเท่านั้น)
    total_games_played INTEGER NOT NULL DEFAULT 1,           -- จำนวนเกมที่เล่นทั้งหมด
    total_wins INTEGER NOT NULL DEFAULT 0,                   -- จำนวนครั้งที่ชนะ
    total_losses INTEGER NOT NULL DEFAULT 0,                 -- จำนวนครั้งที่แพ้
    total_bet_amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00,   -- ยอดเดิมพันรวม
    net_profit_loss NUMERIC(15, 2) NOT NULL DEFAULT 0.00,    -- กำไร/ขาดทุนสุทธิ
    
    played_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- สร้าง unique constraint เพื่อให้แต่ละ user มี record เดียว
ALTER TABLE game1 ADD CONSTRAINT unique_user_game1 UNIQUE (user_id);

-- สร้าง index สำหรับค้นหาข้อมูลเร็วขึ้น
CREATE INDEX IF NOT EXISTS idx_game1_user_id ON game1(user_id);
CREATE INDEX IF NOT EXISTS idx_game1_played_at ON game1(played_at);
CREATE INDEX IF NOT EXISTS idx_game1_total_games ON game1(total_games_played);

-- สร้างตาราง game1_history สำหรับเก็บประวัติการเล่นทุกครั้ง (optional - ถ้าต้องการประวัติโดยละเอียด)
CREATE TABLE IF NOT EXISTS game1_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    bet_amount NUMERIC(10, 2) NOT NULL,
    selected_color VARCHAR(10) NOT NULL,
    result_color VARCHAR(10) NOT NULL,
    won INTEGER NOT NULL,
    win_loss_amount NUMERIC(10, 2) NOT NULL,
    balance_before NUMERIC(10, 2) NOT NULL,
    balance_after NUMERIC(10, 2) NOT NULL,
    played_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- สร้าง index สำหรับ game1_history
CREATE INDEX IF NOT EXISTS idx_game1_history_user_id ON game1_history(user_id);
CREATE INDEX IF NOT EXISTS idx_game1_history_played_at ON game1_history(played_at);

-- สร้าง function สำหรับอัพเดท updated_at อัตโนมัติ
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- สร้าง trigger สำหรับอัพเดท updated_at ใน game1
DROP TRIGGER IF EXISTS update_game1_updated_at ON game1;
CREATE TRIGGER update_game1_updated_at 
    BEFORE UPDATE ON game1 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- สร้าง function สำหรับบันทึกประวัติในตาราง game1_history
CREATE OR REPLACE FUNCTION save_game1_history()
RETURNS TRIGGER AS $$
BEGIN
    -- บันทึกประวัติการเล่นแต่ละครั้งในตาราง history
    INSERT INTO game1_history (
        user_id, bet_amount, selected_color, result_color, won,
        win_loss_amount, balance_before, balance_after, played_at
    ) VALUES (
        NEW.user_id, NEW.bet_amount, NEW.selected_color, NEW.result_color, NEW.won,
        NEW.win_loss_amount, NEW.balance_before, NEW.balance_after, NEW.played_at
    );
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- สร้าง trigger สำหรับบันทึกประวัติอัตโนมัติ
DROP TRIGGER IF EXISTS trigger_save_game1_history ON game1;
CREATE TRIGGER trigger_save_game1_history
    AFTER INSERT OR UPDATE ON game1
    FOR EACH ROW
    EXECUTE FUNCTION save_game1_history();

-- สร้าง view สำหรับดูข้อมูลสถิติผู้เล่นทั้งหมด
CREATE OR REPLACE VIEW game1_player_stats AS
SELECT 
    u.id as user_id,
    u.full_name,
    u.email,
    g.total_games_played,
    g.total_wins,
    g.total_losses,
    g.total_bet_amount,
    g.net_profit_loss,
    CASE 
        WHEN g.total_games_played > 0 
        THEN ROUND((g.total_wins * 100.0 / g.total_games_played), 2)
        ELSE 0 
    END as win_percentage,
    g.played_at as last_played_at,
    g.created_at as first_played_at
FROM users u
LEFT JOIN game1 g ON u.id = g.user_id
WHERE g.user_id IS NOT NULL
ORDER BY g.total_games_played DESC, g.net_profit_loss DESC;

-- Comments สำหรับอธิบายตาราง
COMMENT ON TABLE game1 IS 'ตารางหลักเก็บข้อมูลการเล่นเกม 1 และสถิติของผู้ใช้แต่ละคน (1 user = 1 row)';
COMMENT ON TABLE game1_history IS 'เก็บประวัติการเล่นเกม 1 ทุกครั้งของผู้ใช้ (สำหรับดูประวัติ)';
COMMENT ON COLUMN game1.total_games_played IS 'จำนวนครั้งที่ผู้ใช้เล่นเกมนี้ทั้งหมด';
COMMENT ON COLUMN game1.win_loss_amount IS 'จำนวนเงินที่ชนะ/แพ้ในเกมล่าสุด (+100 ถ้าชนะ, -100 ถ้าแพ้)';
COMMENT ON COLUMN game1.balance_before IS 'ยอดเงินของผู้ใช้ก่อนเล่นเกมล่าสุด';
COMMENT ON COLUMN game1.balance_after IS 'ยอดเงินของผู้ใช้หลังเล่นเกมล่าสุด';
COMMENT ON COLUMN game1.net_profit_loss IS 'กำไร/ขาดทุนสะสมของผู้ใช้จากการเล่นเกมนี้';

-- สร้างข้อมูลตัวอย่าง (สำหรับทดสอบ)
-- หา user_id ที่มีอยู่จริง
DO $$
DECLARE
    test_user_id INTEGER;
BEGIN
    -- หา user ที่มี role = 'user' คนแรก
    SELECT id INTO test_user_id FROM users WHERE role = 'user' LIMIT 1;
    
    IF test_user_id IS NOT NULL THEN
        -- เพิ่มข้อมูลทดสอบ
        INSERT INTO game1 (
            user_id, bet_amount, selected_color, result_color, won, 
            win_loss_amount, balance_before, balance_after,
            total_games_played, total_wins, total_losses, 
            total_bet_amount, net_profit_loss
        ) VALUES (
            test_user_id, 100.00, 'blue', 'blue', 1, 
            100.00, 1000.00, 1100.00,
            3, 2, 1, 
            300.00, 50.00
        ) ON CONFLICT (user_id) DO NOTHING;
        
        RAISE NOTICE 'สร้างข้อมูลทดสอบสำหรับ user_id: %', test_user_id;
    ELSE
        RAISE NOTICE 'ไม่พบ user สำหรับสร้างข้อมูลทดสอบ';
    END IF;
END $$;