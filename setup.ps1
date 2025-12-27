# setup.ps1 - Complete CarSafe Setup Script

Write-Host "🚗 Setting up CarSafe Project..." -ForegroundColor Green

# Step 1: Check Python version
Write-Host "`nStep 1: Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version
Write-Host "Python version: $pythonVersion"

# Step 2: Upgrade pip
Write-Host "`nStep 2: Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to upgrade pip" -ForegroundColor Red
    exit 1
}

# Step 3: Install dependencies
Write-Host "`nStep 3: Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Write-Host "Trying alternative approach..." -ForegroundColor Yellow
    
    # Try installing key packages one by one
    pip install pandas==1.5.3
    pip install fastapi==0.104.1
    pip install uvicorn[standard]==0.24.0
    pip install streamlit==1.28.1
    pip install psycopg2-binary==2.9.9
    pip install kafka-python==2.0.2
}

# Step 4: Test PostgreSQL connection
Write-Host "`nStep 4: Testing PostgreSQL..." -ForegroundColor Yellow
try {
    pip install psycopg2-binary
    Write-Host "✅ PostgreSQL driver installed" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Could not install PostgreSQL driver" -ForegroundColor Yellow
    Write-Host "You may need to install PostgreSQL from: https://www.postgresql.org/download/windows/" -ForegroundColor Cyan
}

# Step 5: Create test files
Write-Host "`nStep 5: Creating test files..." -ForegroundColor Yellow
$testCode = @'
import sys
print(f"Python {sys.version}")
try:
    import pandas
    print(f"✅ pandas {pandas.__version__}")
except ImportError as e:
    print(f"❌ pandas: {e}")

try:
    import fastapi
    print(f"✅ fastapi {fastapi.__version__}")
except ImportError as e:
    print(f"❌ fastapi: {e}")

try:
    import psycopg2
    print("✅ psycopg2 installed")
except ImportError as e:
    print(f"❌ psycopg2: {e}")

try:
    import streamlit
    print(f"✅ streamlit {streamlit.__version__}")
except ImportError as e:
    print(f"❌ streamlit: {e}")
'@

$testCode | Out-File -FilePath "test_installation.py" -Encoding UTF8
python test_installation.py
Remove-Item "test_installation.py"

# Step 6: Initialize project structure
Write-Host "`nStep 6: Creating project structure..." -ForegroundColor Yellow
$folders = @("src", "src/data_generator", "src/kafka_client", "src/api", 
            "src/database", "src/anomaly_detection", "src/utils",
            "tests", "dashboard")

foreach ($folder in $folders) {
    if (!(Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "  Created: $folder"
    }
}

# Step 7: Success message
Write-Host "`n" + "="*50 -ForegroundColor Cyan
Write-Host "✅ CarSafe Setup Complete!" -ForegroundColor Green
Write-Host "="*50 -ForegroundColor Cyan

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Install PostgreSQL if not already installed" -ForegroundColor White
Write-Host "2. Run: python src/database/setup.py" -ForegroundColor White
Write-Host "3. Run: python src/kafka_client/producer.py" -ForegroundColor White
Write-Host "4. Run: uvicorn src.api.main:app --reload" -ForegroundColor White
Write-Host "5. Open: http://localhost:8000/docs" -ForegroundColor White