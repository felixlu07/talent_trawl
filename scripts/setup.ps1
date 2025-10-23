# Talent Trawler Setup Script for Windows
# This script sets up the virtual environment and installs dependencies

Write-Host "🎯 Talent Trawler Setup" -ForegroundColor Cyan
Write-Host "=" * 60

# Check Python installation
Write-Host "`n📋 Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green

# Create virtual environment
Write-Host "`n📦 Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  Virtual environment already exists. Skipping creation." -ForegroundColor Yellow
} else {
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`n🔄 Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "`n⬆️  Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Install dependencies
Write-Host "`n📥 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ All dependencies installed successfully!" -ForegroundColor Green

# Check for .env file
Write-Host "`n🔑 Checking configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ .env file found" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
    Write-Host "   Please ensure your .env file contains:" -ForegroundColor Yellow
    Write-Host "   ANTHROPIC_API_KEY=your_api_key_here" -ForegroundColor White
    Write-Host "   ANTHROPIC_MODEL=claude-sonnet-4-5-20250929" -ForegroundColor White
}

# Check for Poppler
Write-Host "`n📚 Checking Poppler installation..." -ForegroundColor Yellow
$popplerCheck = Get-Command pdftoppm -ErrorAction SilentlyContinue
if ($popplerCheck) {
    Write-Host "✅ Poppler found in PATH" -ForegroundColor Green
} else {
    Write-Host "⚠️  Poppler not found in PATH" -ForegroundColor Yellow
    Write-Host "   Download from: https://github.com/oschwartz10612/poppler-windows/releases/" -ForegroundColor White
    Write-Host "   Extract and add bin/ folder to your system PATH" -ForegroundColor White
}

Write-Host "`n" + "=" * 60
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host "=" * 60

Write-Host "`n📝 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Ensure Poppler is installed (if not already)" -ForegroundColor White
Write-Host "   2. Create example config: python talent_trawler.py --create-example test_folder" -ForegroundColor White
Write-Host "   3. Add PDF resumes to the folder" -ForegroundColor White
Write-Host "   4. Run analysis: python talent_trawler.py test_folder" -ForegroundColor White
Write-Host ""
