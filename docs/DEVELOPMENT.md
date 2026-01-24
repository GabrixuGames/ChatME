# Development Guide

## Overview
ChatME is a real-time chat app with a React + TypeScript frontend and a Flask + Socket.IO backend. PostgreSQL is used for persistence.

## Project Structure (High Level)
```
backend/   # Flask app, routes, services, repositories, tests
frontend/  # React app
database/  # SQL schema + migrations + indexes
docs/      # Project documentation
```

## Environment Configuration
Backend uses environment variables from `backend/.env` (copy from `backend/.env.example`).
Required secrets:
- `JWT_SECRET` (min 32 chars)
- `FLASK_SECRET_KEY` (min 32 chars)

Generate secure secrets:
```bash
openssl rand -base64 32
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Frontend uses `frontend/.env` (copy from `frontend/.env.example`).

## Database (Docker)
Docker Compose is defined in `docker-compose.yml` at the repo root.
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

## Tests
Backend tests require a running Postgres instance.
```bash
cd backend
python tests/run_tests.py
```

## Team Workflow (Condensed)
- Use clear, concise communication; mention the role when requesting input.
- Priorities: correctness, security, performance, maintainability.
- Seniors review junior code before merge.

## Coding Standards (Condensed)
- Naming: snake_case (Python), camelCase (JS/TS), PascalCase (classes/components).
- Keep functions focused; avoid overly long methods.
- Use parameterized SQL, sanitize inputs, and log errors responsibly.

## Git Conventions
- Branches: `feature/`, `bugfix/`, `hotfix/`, `release/`
- Commits: conventional commits (feat, fix, docs, refactor, test, perf)
