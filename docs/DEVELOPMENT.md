# Development Guide

## Overview
ChatME is a real-time chat app with a React + TypeScript frontend and a Flask + Socket.IO backend. PostgreSQL stores users, rooms, and messages.

## Project Layout
```
backend/   # Flask app, routes, services, repositories, tests
frontend/  # React app (Vite)
database/  # SQL schema + migrations + indexes
docs/      # Central documentation
```

## Environment Configuration
Backend uses `backend/.env` (copy from `backend/.env.example`).

Required:
- `JWT_SECRET` (min 32 chars)
- `FLASK_SECRET_KEY` (min 32 chars)

Common:
- `ENVIRONMENT` / `FLASK_ENV` (`development` | `production`)
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT`
- `CORS_ALLOWED_ORIGINS` or `CORS_ORIGINS` (comma-separated)
- `RATE_LIMITS` (comma-separated, optional)

Generate secure secrets:
```bash
openssl rand -base64 32
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Frontend uses `frontend/.env` (copy from `frontend/.env.example`):
- `VITE_API_URL`
- `VITE_SOCKET_URL`

## Database (Docker)
`docker-compose.yml` is at repo root.
```bash
docker-compose up -d
docker ps
```

Common commands:
```bash
docker-compose logs postgres
docker-compose down
docker exec -it chatapp-postgres psql -U chatapp -d chatapp
```

## Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

## Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Local Network Access
To access from another device:
1) Start Vite with `npm run dev -- --host 0.0.0.0`
2) Set `VITE_API_URL` and `VITE_SOCKET_URL` to your LAN IP (e.g. `http://192.168.1.50:5000`)
3) Add that IP to `CORS_ALLOWED_ORIGINS` on the backend

## API Endpoints (Summary)
- Auth: `POST /register`, `POST /procesar_login`, `POST /logout`
- Rooms: `GET /chat/rooms`, `POST /chat/mark_read`, `POST /chat/hide_room`
- Private chat: `POST /chat/individual/create`, `POST /chat/individual/delete`, `POST /chat/individual/cleanup_temporary`
- Friends: `GET /friends/list`, `GET /friends/pending`, `GET /friends/sent`
- Requests: `POST /friends/send_request`, `POST /friends/respond_request`, `POST /friends/remove`
- Search: `GET /friends/search?query=...`

## Tests
Backend tests require a running Postgres instance.
```bash
cd backend
python tests/run_tests.py
```

## Team Workflow (Condensed)
- Communicate clearly, and mention the role when requesting input.
- Priorities: correctness, security, performance, maintainability.
- Seniors review junior code before merge.

## Coding Standards (Condensed)
- Naming: snake_case (Python), camelCase (JS/TS), PascalCase (classes/components).
- Keep functions focused and avoid overly long methods.
- Use parameterized SQL, sanitize inputs, and log errors responsibly.

## Git Conventions
- Branches: `feature/`, `bugfix/`, `hotfix/`, `release/`
- Commits: conventional commits (feat, fix, docs, refactor, test, perf)
