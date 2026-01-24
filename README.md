# ChatME

Real-time chat with public rooms and private conversations, built with React + TypeScript and Flask + Socket.IO, backed by PostgreSQL.

## Highlights
- Real-time messaging with Socket.IO
- Public rooms + private chats
- Dual chat windows (drag & drop to open in parallel)
- Responsive UI for mobile, tablet, and desktop
- JWT auth + bcrypt password hashing

## Screenshots
Add project screenshots in `docs/assets/` and update this section (suggested files: `profile-desktop.png`, `profile-mobile.png`, `dual-chat.png`).

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

## Architecture
- `frontend/`: React UI (Vite), real-time UI via Socket.IO client
- `backend/`: Flask API + Socket.IO, services/repositories layered
- `database/`: schema, migrations, and indexes

## Documentation
- `docs/DEVELOPMENT.md` - setup, env vars, workflow, and standards
- `docs/SECURITY.md` - auth, data handling, and security guarantees
- `docs/CHANGELOG.md` - notable changes by date

## Tech Stack
- Backend: Python, Flask, Flask-SocketIO, PostgreSQL
- Frontend: React, TypeScript, Vite, TailwindCSS

## Tests
```bash
cd backend
python tests/run_tests.py
```
