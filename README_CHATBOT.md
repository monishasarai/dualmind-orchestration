# Claude-Style Chatbot Interface

A calm, minimal chatbot experience inspired by Anthropic’s Claude. The frontend is built with React, TypeScript, Vite, and Tailwind CSS; the backend extends the existing FastAPI orchestrator with secure chat and upload endpoints.

## Features

- 💬 Text conversation with Claude-inspired assistant tone
- 📁 Upload JPG, PNG, or PDF files (10 MB limit) and ask follow-up questions
- 🧠 Integrates with the existing `Orchestrator` pipeline for responses
- 🪄 Smooth auto-scroll, typing indicators, and subtle animations
- 💾 Chat history persisted in `localStorage`
- 🔒 Input sanitisation, MIME checks, and temporary storage under `/uploads`

## Tech Stack

- **Backend:** FastAPI (`api_server.py`) + existing orchestrator tools
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS
- **HTTP Client:** Axios
- **Styling:** Tailwind tokens configured for a soft neutral palette

## Setup

### 1. Backend

```bash
pip install -r requirements.txt

# Start the API (runs on http://localhost:8000)
python api_server.py
```

Optional environment overrides:

```bash
export API_PORT=8000
export API_HOST=0.0.0.0
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

The development server runs at `http://localhost:5173` and proxies `/api` to the backend.

## API Overview

| Method | Endpoint       | Description                             |
| ------ | -------------- | --------------------------------------- |
| POST   | `/api/chat`    | Submit a text message for assistant reply |
| POST   | `/api/upload`  | Upload a JPG/PNG/PDF with optional prompt |
| GET    | `/api/health`  | Health check                             |

Uploads are stored in `/uploads`. PDF files are parsed with `PDFParserTool` to provide context in follow-up questions.

## Claude-Style Design Notes (Dark Edition)

- **Palette:** Near-black gradients (`#050505`, `#0B0B0F`) for the canvas, deep graphite panels (`#11131A`), and electric yellow accents (`#F5D300`, `#F8E25A`). Primary text stays soft-white (`#F5F5F5`) with muted grays for secondary copy.
- **Layout:** Centered column, rounded 24 px container, subtle panel shadow, glass effect using translucent dark panels and crisp borders.
- **Typography:** Inter 15 px base, generous line height, uppercase timestamp badges.
- **Interactions:** Fade-in for new messages, soft hover lifts, pulse animation for typing indicator, accent glow on primary actions.

Tailwind tokens live in `frontend/tailwind.config.js`, while reusable theme values are exported from `frontend/src/theme.ts`.

## Development Tips

- Set `VITE_API_URL` in `frontend/.env` if the backend runs on a different origin.
- Run `uvicorn api_server:app --reload --port 8000` for hot-reload during backend development.
- Use `npm run build` in `frontend` to produce a production-ready bundle under `frontend/dist`.

## Security Considerations

- User input is trimmed and sanitized before hitting the orchestrator.
- File uploads are validated for MIME type and size, stored with timestamped names.
- Configure HTTPS and production-grade CORS rules when deploying externally.

Enjoy the Claude-style conversational experience! 🤝
