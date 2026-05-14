# DualMind Setup Instructions

## Prerequisites
- Python 3.8+ with conda
- Node.js 18+ and npm
- Virtual environment named "shreya" (conda)

## Quick Start

### Option 1: Using PowerShell Scripts (Recommended)

**Terminal 1 - Backend:**
```powershell
# From project root
.\start_backend.ps1
```

**Terminal 2 - Frontend:**
```powershell
# From project root
.\start_frontend.ps1
```

### Option 2: Manual Setup

**Terminal 1 - Backend:**
```powershell
# Navigate to project root
cd C:\Users\shrey\JARVIS-DOMAIN-SPECIFIC-V1

# Activate conda environment
conda activate shreya

# Install Python dependencies (if not already installed)
pip install -r requirements.txt

# Start API server
python api_server.py
```

**Terminal 2 - Frontend:**
```powershell
# Navigate to frontend directory
cd C:\Users\shrey\JARVIS-DOMAIN-SPECIFIC-V1\frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

## Access the Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## Important Notes

1. **Backend must run from project root** - `api_server.py` is in the root directory, not in `frontend/`
2. **Virtual environment** - Make sure the "shreya" conda environment is activated before running the backend
3. **Two terminals needed** - Backend and frontend run separately
4. **First time setup** - Run `npm install` in the frontend directory before starting the dev server

## Troubleshooting

**Error: "No such file or directory"**
- Make sure you're in the project root directory when running `python api_server.py`
- Check that `api_server.py` exists in the current directory

**Error: "Module not found"**
- Activate the conda environment: `conda activate shreya`
- Install dependencies: `pip install -r requirements.txt`

**Frontend won't start**
- Make sure you're in the `frontend` directory
- Run `npm install` if `node_modules` doesn't exist
- Check that Node.js 18+ is installed

