# Game1 Development Server Starter
# รัน script นี้เพื่อเริ่ม backend และ frontend พร้อมกัน

Write-Host "🚀 Starting X-BET Game1 Development Environment" -ForegroundColor Cyan
Write-Host "=" * 60

# ตรวจสอบว่า Docker รันอยู่หรือไม่
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker first." -ForegroundColor Red
    pause
    exit 1
}

# ตรวจสอบว่า Node.js รันอยู่หรือไม่
try {
    node --version | Out-Null
    Write-Host "✅ Node.js is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed. Please install Node.js first." -ForegroundColor Red
    pause
    exit 1
}

# ตรวจสอบว่า Python รันอยู่หรือไม่
try {
    python --version | Out-Null
    Write-Host "✅ Python is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed. Please install Python first." -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""

# ฟังก์ชันสำหรับรัน backend
function Start-Backend {
    Write-Host "🔧 Starting Backend Server..." -ForegroundColor Yellow
    
    # ติดตั้ง dependencies ถ้ายังไม่ได้ติดตั้ง
    if (-not (Test-Path "backend\venv")) {
        Write-Host "📦 Creating Python virtual environment..." -ForegroundColor Cyan
        cd backend
        python -m venv venv
        .\venv\Scripts\Activate.ps1
        pip install -r requirements.txt
        cd ..
    }
    
    # เริ่ม backend server
    cd backend
    .\venv\Scripts\Activate.ps1
    Write-Host "🌐 Backend starting at http://localhost:8000" -ForegroundColor Green
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# ฟังก์ชันสำหรับรัน frontend
function Start-Frontend {
    Write-Host "🎨 Starting Frontend Server..." -ForegroundColor Yellow
    
    # ติดตั้ง dependencies ถ้ายังไม่ได้ติดตั้ง
    if (-not (Test-Path "frontend\node_modules")) {
        Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Cyan
        cd frontend
        npm install
        cd ..
    }
    
    # เริ่ม frontend server
    cd frontend
    Write-Host "🌐 Frontend starting at http://localhost:3000" -ForegroundColor Green
    npm run dev
}

# ฟังก์ชันสำหรับรัน database
function Start-Database {
    Write-Host "🗄️ Starting Database..." -ForegroundColor Yellow
    
    # ตรวจสอบว่า docker-compose.yml มีอยู่หรือไม่
    if (Test-Path "docker-compose.yml") {
        Write-Host "🐳 Starting PostgreSQL with Docker..." -ForegroundColor Cyan
        docker-compose up -d
        Start-Sleep -Seconds 5
        Write-Host "✅ Database started successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠️ docker-compose.yml not found. Please make sure database is running." -ForegroundColor Yellow
    }
}

# เมนูหลัก
do {
    Clear-Host
    Write-Host "🎮 X-BET Game1 Development Menu" -ForegroundColor Cyan
    Write-Host "=" * 40
    Write-Host "1. Start Database Only" -ForegroundColor White
    Write-Host "2. Start Backend Only" -ForegroundColor White  
    Write-Host "3. Start Frontend Only" -ForegroundColor White
    Write-Host "4. Start All Services" -ForegroundColor White
    Write-Host "5. Open Game1 Tester (HTML)" -ForegroundColor White
    Write-Host "6. Open Game1 Web Interface" -ForegroundColor White
    Write-Host "7. Setup Game1 Database" -ForegroundColor White
    Write-Host "8. Run Python API Test" -ForegroundColor White
    Write-Host "0. Exit" -ForegroundColor Red
    Write-Host ""
    
    $choice = Read-Host "Select option (0-8)"
    
    switch ($choice) {
        "1" {
            Start-Database
            Write-Host "Press any key to continue..." -ForegroundColor Gray
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        "2" {
            Start-Backend
        }
        "3" {
            Start-Frontend  
        }
        "4" {
            Write-Host "🚀 Starting All Services..." -ForegroundColor Cyan
            
            # เริ่ม Database ก่อน
            Start-Database
            
            Write-Host "⏳ Waiting for services to initialize..." -ForegroundColor Yellow
            Start-Sleep -Seconds 3
            
            # เริ่ม Backend และ Frontend พร้อมกัน
            Write-Host "🔧 Starting Backend and Frontend servers..." -ForegroundColor Yellow
            Write-Host "📝 Note: This will open multiple terminal windows" -ForegroundColor Cyan
            
            # เริ่ม Backend ใน terminal ใหม่
            Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
            
            Start-Sleep -Seconds 2
            
            # เริ่ม Frontend ใน terminal ใหม่  
            Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev"
            
            Write-Host ""
            Write-Host "✅ All services started!" -ForegroundColor Green
            Write-Host "🌐 Backend: http://localhost:8000" -ForegroundColor Cyan
            Write-Host "🎨 Frontend: http://localhost:3000" -ForegroundColor Cyan
            Write-Host "🎮 Game1: http://localhost:3000/game1" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "Press any key to return to menu..." -ForegroundColor Gray
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        "5" {
            if (Test-Path "game1_tester.html") {
                Write-Host "🌐 Opening Game1 Tester..." -ForegroundColor Green
                Start-Process "game1_tester.html"
            } else {
                Write-Host "❌ game1_tester.html not found" -ForegroundColor Red
            }
            Start-Sleep -Seconds 2
        }
        "6" {
            Write-Host "🌐 Opening Game1 Web Interface..." -ForegroundColor Green
            Start-Process "http://localhost:3000/game1"
            Start-Sleep -Seconds 2
        }
        "7" {
            Write-Host "🗄️ Setting up Game1 Database..." -ForegroundColor Yellow
            if (Test-Path "setup_game1_database.py") {
                python setup_game1_database.py
            } else {
                Write-Host "❌ setup_game1_database.py not found" -ForegroundColor Red
            }
            Write-Host "Press any key to continue..." -ForegroundColor Gray
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        "8" {
            Write-Host "🧪 Running Python API Test..." -ForegroundColor Yellow
            if (Test-Path "test_game1.py") {
                python test_game1.py
            } else {
                Write-Host "❌ test_game1.py not found" -ForegroundColor Red
            }
            Write-Host "Press any key to continue..." -ForegroundColor Gray
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        "0" {
            Write-Host "👋 Goodbye!" -ForegroundColor Cyan
            break
        }
        default {
            Write-Host "❌ Invalid option. Please try again." -ForegroundColor Red
            Start-Sleep -Seconds 2
        }
    }
} while ($choice -ne "0")

Write-Host ""
Write-Host "🎉 Thanks for using X-BET Game1 Development Environment!" -ForegroundColor Green