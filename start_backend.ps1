# DualMind Backend Startup Script for Windows PowerShell
# Run this from the project root directory

Write-Host "🚀 Starting DualMind API Server..." -ForegroundColor Cyan

# Activate conda environment (if not already active)
Write-Host "📦 Activating conda environment 'shreya'..." -ForegroundColor Yellow
conda activate shreya

# Check if we're in the right directory
if (-not (Test-Path "api_server.py")) {
    Write-Host "❌ Error: api_server.py not found. Make sure you're in the project root directory." -ForegroundColor Red
    exit 1
}

# Start the API server
Write-Host "🌐 Starting FastAPI server on http://localhost:8000..." -ForegroundColor Green
python api_server.py

