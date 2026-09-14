# AutoOps AI Setup Script

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "AutoOps AI Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Create directories
Write-Host "Creating directories..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path "data\processed", "data\raw", "logs", "backend\data\processed" | Out-Null

# Check Python version
$pythonVersion = py --version 2>&1
Write-Host "Python version: $pythonVersion" -ForegroundColor Green

# Determine requirements file
$requirementsFile = "requirements.txt"
if ($pythonVersion -like "*3.14*") {
    Write-Host "WARNING: Python 3.14 detected. Using minimal requirements." -ForegroundColor Yellow
    $requirementsFile = "requirements-minimal.txt"
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Green
if (-not (Test-Path "venv")) {
    py -m venv venv
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Green
& .\venv\Scripts\python.exe -m pip install --upgrade pip -q
& .\venv\Scripts\pip.exe install -r $requirementsFile -q

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
    exit 1
}

# Initialize RBAC database
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Initializing RBAC System" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Setting up Role-Based Access Control..." -ForegroundColor White

$currentDir = Get-Location
Set-Location backend

try {
    $initDbOutput = & ..\venv\Scripts\python.exe init_db.py 2>&1
    $initDbExitCode = $LASTEXITCODE
    
    Write-Host $initDbOutput
    
    if ($initDbExitCode -eq 0) {
        Write-Host ""
        Write-Host "[OK] RBAC System initialized successfully!" -ForegroundColor Green
        Write-Host "   Database: backend\data\processed\it_support_systems.db" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Admin User Credentials:" -ForegroundColor Yellow
        Write-Host "  Email:    admin@acme.com" -ForegroundColor White
        Write-Host "  Password: admin123" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "⚠️  RBAC database initialization had issues" -ForegroundColor Yellow
        Write-Host "   The system will still work, but user authentication may not be available." -ForegroundColor Yellow
        Write-Host "   You can retry later by running:" -ForegroundColor Cyan
        Write-Host "   cd backend; ..\venv\Scripts\python.exe init_db.py" -ForegroundColor White
    }
} finally {
    Set-Location $currentDir
}

# Setup .env file
if (-not (Test-Path "backend\.env")) {
    if (Test-Path "backend\.env.example") {
        Copy-Item "backend\.env.example" "backend\.env"
        Write-Host "Created backend\.env from example" -ForegroundColor Green
        Write-Host "⚠️  IMPORTANT: Edit backend\.env and add your GOOGLE_API_KEY before the vector database can be created!" -ForegroundColor Yellow
    } else {
        Write-Host "WARNING: No .env.example found. Please create backend\.env manually." -ForegroundColor Yellow
    }
}

# Check if required data file exists
$dataFile = "backend\data\raw\ticketing_system_data_new.json"
if (-not (Test-Path $dataFile)) {
    Write-Host ""
    Write-Host "⚠️  WARNING: Required data file not found: $dataFile" -ForegroundColor Yellow
    Write-Host "Vector database creation will be skipped." -ForegroundColor Yellow
    Write-Host "Please add the data file and run: .\venv\Scripts\python.exe backend\ingestion_script.py" -ForegroundColor Cyan
} else {
    # Check if GOOGLE_API_KEY is configured
    $envContent = Get-Content "backend\.env" -ErrorAction SilentlyContinue
    $hasApiKey = $envContent | Where-Object { $_ -match "^GOOGLE_API_KEY=.+(?<!your-google-api-key-here)$" }
    
    if (-not $hasApiKey) {
        Write-Host ""
        Write-Host "⚠️  GOOGLE_API_KEY not configured in backend\.env" -ForegroundColor Yellow
        Write-Host "Skipping vector database creation." -ForegroundColor Yellow
        Write-Host "To create the vector database later:" -ForegroundColor Cyan
        Write-Host "  1. Add your GOOGLE_API_KEY to backend\.env" -ForegroundColor White
        Write-Host "  2. Run: .\venv\Scripts\python.exe backend\ingestion_script.py" -ForegroundColor White
    } else {
        # Initialize vector database
        Write-Host ""
        Write-Host "=========================================" -ForegroundColor Cyan
        Write-Host "Creating Vector Database" -ForegroundColor Cyan
        Write-Host "=========================================" -ForegroundColor Cyan
        Write-Host "This will create embeddings from the ticket data..." -ForegroundColor White
        Write-Host "This may take a few minutes depending on data size..." -ForegroundColor White
        Write-Host ""

        Set-Location backend

        $ingestionOutput = & ..\venv\Scripts\python.exe ingestion_script.py 2>&1
        $ingestionExitCode = $LASTEXITCODE

        Write-Host $ingestionOutput

        Set-Location ..

        if ($ingestionExitCode -eq 0) {
            Write-Host ""
            Write-Host "✅ Vector database created successfully!" -ForegroundColor Green
            Write-Host "   Location: backend\data\processed\chroma_db" -ForegroundColor Gray
        } else {
            Write-Host ""
            Write-Host "❌ Vector database creation failed!" -ForegroundColor Red
            Write-Host "   Please check the error messages above." -ForegroundColor Yellow
            Write-Host "   You can retry later by running:" -ForegroundColor Cyan
            Write-Host "   .\venv\Scripts\python.exe backend\ingestion_script.py" -ForegroundColor White
        }
    }
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Components Installed:" -ForegroundColor Yellow

# Check RBAC database
if (Test-Path "backend\data\processed\it_support_systems.db") {
    Write-Host "[OK] RBAC Database initialized" -ForegroundColor Green
} else {
    Write-Host "[!] RBAC Database not initialized" -ForegroundColor Yellow
}

# Check if vector DB was created
if (Test-Path "backend\data\processed\chroma_db") {
    Write-Host "✅ Vector database ready" -ForegroundColor Green
} else {
    Write-Host "⚠️  Vector database not yet created" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow

if (Test-Path "backend\data\processed\chroma_db") {
    Write-Host "To start the application:" -ForegroundColor Cyan
    Write-Host "  .\run.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "API will be available at:" -ForegroundColor Cyan
    Write-Host "  http://localhost:8000" -ForegroundColor White
    Write-Host "  http://localhost:8000/docs (API Documentation)" -ForegroundColor White
} else {
    Write-Host "To create the vector database:" -ForegroundColor Cyan
    Write-Host "  1. Ensure data file exists: backend\data\raw\ticketing_system_data_new.json" -ForegroundColor White
    Write-Host "  2. Add your GOOGLE_API_KEY to backend\.env" -ForegroundColor White
    Write-Host "  3. Run: .\venv\Scripts\python.exe backend\ingestion_script.py" -ForegroundColor White
    Write-Host ""
    Write-Host "Then start the application:" -ForegroundColor Cyan
    Write-Host "  .\run.ps1" -ForegroundColor White
}

Write-Host ""
