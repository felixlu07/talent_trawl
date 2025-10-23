# Quick run script for Talent Trawler
# Usage: .\run.ps1 <folder_name>

param(
    [Parameter(Mandatory=$true)]
    [string]$FolderPath
)

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "⚠️  Virtual environment not found. Run setup.ps1 first." -ForegroundColor Yellow
}

# Run Talent Trawler
Write-Host "🎯 Running Talent Trawler on: $FolderPath" -ForegroundColor Cyan
python talent_trawler.py $FolderPath
