# AI Edu Assessment (Web App)

## Overview
Full-stack implementation with:
- Backend: FastAPI (Python), SQLite storage, optional Gemini integration
- Frontend: Next.js (Vercel-ready)

## Backend (FastAPI)
Location: `backend/`

### Setup
1. Python 3.10+
2. Install deps:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Env vars (create `.env` next to `backend/main.py` or export):
   - `DB_PATH` (default: `data/projects.db`)
   - `CORS_ORIGINS` (comma-separated, e.g. `https://your-frontend.vercel.app,http://localhost:3000`)
   - `GEMINI_API_KEY` (optional, for better glossary/quiz quality)

### Run
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
Expose with ngrok and use the HTTPS URL in the frontend:
```bash
ngrok http 8000
```

### Endpoints
- `GET /health`
- `POST /analyze` { text, language, num_questions }
- `POST /analyze/upload` (multipart: file, language, num_questions)
- `GET /sessions`
- `GET /sessions/{id}`

## Frontend (Next.js)
Location: `frontend/`

### Setup
```bash
cd frontend
npm install
```

Create env var for backend URL (local or ngrok):
- On local dev: create `.env.local`
  ```env
  NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
  ```
- On Vercel: Project Settings → Environment Variables → `NEXT_PUBLIC_BACKEND_URL`

### Run
```bash
npm run dev
```

### Build for Vercel
Push `frontend/` to your Vercel project root or select it during import. Build command `npm run build`, output `.next` (default).

## Notes
- If you provide `GEMINI_API_KEY`, the backend will call Gemini (1.5/2.5 Flash-compatible REST endpoint) to improve definitions and question generation.
- Without the key, the app uses heuristic fallbacks so it still works offline.

## Folder Structure
See `backend/` and `frontend/` directories.

