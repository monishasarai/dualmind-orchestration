# DualMind Frontend Startup Script for Windows PowerShell
# Run this from the project root directory

Write-Host "🎨 Starting DualMind Frontend..." -ForegroundColor Cyan

# Navigate to frontend directory
if (-not (Test-Path "frontend")) {
    Write-Host "❌ Error: frontend directory not found. Make sure you're in the project root directory." -ForegroundColor Red
    exit 1
}

Set-Location frontend

# Check if node_modules exists, if not, install dependencies
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Start the development server
Write-Host "🌐 Starting Vite dev server on http://localhost:5173..." -ForegroundColor Green
npm run dev

