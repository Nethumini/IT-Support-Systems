# IT Support Systems Run Script

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "IT Support Systems Server" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Run setup first: .\setup.ps1" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
& .\venv\Scripts\Activate.ps1

# Check .env file
if (-not (Test-Path "backend\.env")) {
    Write-Host "WARNING: backend\.env not found!" -ForegroundColor Yellow
    Write-Host "Copy backend\.env.example and add your API keys" -ForegroundColor Yellow
}

# Start server
Write-Host ""
Write-Host "Starting server..." -ForegroundColor Green
Write-Host "API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press CTRL+C to stop" -ForegroundColor Yellow
Write-Host ""

Set-Location backend
& ..\venv\Scripts\python.exe -m uvicorn app.main:app --reload
