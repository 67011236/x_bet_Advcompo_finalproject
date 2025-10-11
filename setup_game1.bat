@echo off
echo ====================================
echo Game1 Database Setup for X-BET
echo ====================================
echo.

REM ตรวจสอบว่า Python มีหรือไม่
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python ไม่พบในระบบ กรุณาติดตั้ง Python ก่อน
    pause
    exit /b 1
)

echo ✅ Python พบแล้ว

REM ติดตั้ง dependencies
echo.
echo 📦 Installing Python packages...
pip install -r game1_requirements.txt

if %ERRORLEVEL% neq 0 (
    echo ❌ การติดตั้ง packages ล้มเหลว
    pause
    exit /b 1
)

echo ✅ Packages installed successfully

REM ตรวจสอบไฟล์ SQL
if not exist "create_game1_tables.sql" (
    echo ❌ ไม่พบไฟล์ create_game1_tables.sql
    pause
    exit /b 1
)

echo ✅ SQL file พบแล้ว

REM ถาม environment variables
echo.
echo ⚙️  กรุณาตั้งค่า Database connection:
echo (กด Enter เพื่อใช้ค่า default)
echo.

set /p DB_HOST="DB Host (localhost): "
if "%DB_HOST%"=="" set DB_HOST=localhost

set /p DB_PORT="DB Port (5432): "
if "%DB_PORT%"=="" set DB_PORT=5432

set /p DB_NAME="DB Name (xbet_db): "
if "%DB_NAME%"=="" set DB_NAME=xbet_db

set /p DB_USER="DB User (postgres): "
if "%DB_USER%"=="" set DB_USER=postgres

set /p DB_PASSWORD="DB Password: "
if "%DB_PASSWORD%"=="" set DB_PASSWORD=password

REM Export environment variables
set DB_HOST=%DB_HOST%
set DB_PORT=%DB_PORT%
set DB_NAME=%DB_NAME%
set DB_USER=%DB_USER%
set DB_PASSWORD=%DB_PASSWORD%

echo.
echo 🔗 Connecting to: %DB_USER%@%DB_HOST%:%DB_PORT%/%DB_NAME%

REM รัน setup script
echo.
echo 🚀 Running database setup...
python setup_game1_database.py

if %ERRORLEVEL% neq 0 (
    echo ❌ Database setup ล้มเหลว
    pause
    exit /b 1
)

echo.
echo ✅ Game1 database setup completed!
echo.
echo 📋 สิ่งที่ถูกสร้าง:
echo    - ตาราง game1 (เก็บข้อมูลการเล่นแต่ละครั้ง)
echo    - ตาราง game1_stats (เก็บสถิติของผู้ใช้)
echo    - Functions และ Triggers สำหรับอัพเดทสถิติอัตโนมัติ
echo    - API endpoints ใน backend/app/main.py
echo.
echo 🎮 คุณสามารถเริ่มเล่น Game1 ได้แล้ว!
echo.
echo 📚 สำหรับคู่มือการใช้งาน ดูได้ที่:
echo    - GAME1_README.md
echo    - test_game1.py (สำหรับทดสอบ)
echo.

pause