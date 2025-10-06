-- SQL script สำหรับลบ table 'details' ใน PostgreSQL
-- วิธีใช้: รันใน DBeaver Query Editor

-- ตรวจสอบว่ามี table details หรือไม่
SELECT table_name 
FROM information_schema.tables 
WHERE table_name = 'details' AND table_schema = 'public';

-- ดูข้อมูลใน table details (หากมี)
-- SELECT * FROM details;

-- ลบ table details (ยกเลิก comment หากต้องการรัน)
-- DROP TABLE IF EXISTS details CASCADE;

-- ตรวจสอบ tables ที่เหลือ
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;