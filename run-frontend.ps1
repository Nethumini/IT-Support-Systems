# AutoOps AI Frontend Run Script

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "AutoOps AI Frontend" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check if node_modules exists
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
        exit 1
    }
    Set-Location ..
}

# Start frontend
Write-Host ""
Write-Host "Starting frontend dev server..." -ForegroundColor Green
Write-Host "Frontend will be available at: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press CTRL+C to stop" -ForegroundColor Yellow
Write-Host ""

Set-Location frontend
npm run dev
