# DualMind Quick Start Guide

## ✅ Prerequisites Installed
- ✅ PyPDF2
- ✅ pdfplumber
- ✅ All other dependencies from requirements.txt

## 🚀 Start the Application

### Step 1: Start Backend (Terminal 1)

```powershell
# Navigate to project root
cd C:\Users\shrey\JARVIS-DOMAIN-SPECIFIC-V1

# Activate conda environment
conda activate shreya

# Start API server
python api_server.py
```

You should see:
```
INFO:     Started server process [...]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Start Frontend (Terminal 2 - NEW WINDOW)

```powershell
# Navigate to frontend directory
cd C:\Users\shrey\JARVIS-DOMAIN-SPECIFIC-V1\frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

## 🌐 Access the Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## ⚠️ Troubleshooting

### Port 8000 Already in Use
If you get `[Errno 10048]`, port 8000 is already in use:

```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with the number from above)
Stop-Process -Id <PID> -Force
```

### Missing Dependencies
If you see "PyPDF2 not installed" or similar:

```powershell
conda activate shreya
pip install -r requirements.txt
```

### Frontend Won't Start
```powershell
cd frontend
npm install
npm run dev
```

## 📝 Notes

- **Two terminals needed**: Backend and frontend run separately
- **Backend runs from root**: `api_server.py` is in the project root, not in `frontend/`
- **PyTorch warnings are OK**: The server will work even if you see PyTorch warnings (they're just about model loading)

## 🎉 You're Ready!

Once both servers are running:
1. Open http://localhost:5173 in your browser
2. Click "Try Now" on the home page
3. Start chatting with DualMind!

