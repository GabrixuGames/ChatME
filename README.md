# ChatME - Real-Time Chat Application

A real-time chat application with a React + TypeScript frontend and a Flask + Socket.IO backend, backed by PostgreSQL.

## Quick Start
```bash
# Database
docker-compose up -d

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python app.py

# Frontend
cd ../frontend
npm install
cp .env.example .env
npm run dev
```

## Documentation
- `docs/DEVELOPMENT.md` - setup, workflow, and coding standards
- `docs/SECURITY.md` - security guarantees and references
- `docs/CHANGELOG.md` - recent refactors

## Tech Stack
- Backend: Python, Flask, Flask-SocketIO, PostgreSQL
- Frontend: React, TypeScript, Vite
