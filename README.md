# ChatME

Aplicacion de chat en tiempo real con salas publicas y conversaciones privadas, construida con React + TypeScript y Flask + Socket.IO, respaldada por PostgreSQL.

---

## 📌 Tabla de contenidos
- [Descripción](#-descripción)
- [Características](#-características)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Configuración](#-configuración)
- [Estado del proyecto](#-estado-del-proyecto)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

---

## 📖 Descripción

ChatME permite crear salas publicas y chats privados con mensajeria en tiempo real.
Pensado para equipos o comunidades que necesitan comunicacion rapida con una interfaz sencilla, responsive y multiplataforma.
El proyecto existe para ofrecer una base limpia y extensible con foco en seguridad y mantenibilidad.

---

## ✨ Características

- ✔️ Mensajeria en tiempo real con Socket.IO
- ✔️ Salas publicas y chats privados
- ✔️ Doble ventana de chat (drag & drop)
- ✔️ UI responsive para movil, tablet y desktop
- ✔️ Autenticacion con JWT y passwords hasheadas con bcrypt
- ✔️ Codigo claro y documentacion centralizada

---

## 📸 Capturas

| Index | Login |
| --- | --- |
| ![Perfil desktop](docs/assets/Captura%20desde%202026-01-24%2015-05-09.png) | ![Perfil mobile](docs/assets/Captura%20desde%202026-01-24%2015-05-17.png) |

| Profile | Parallel chat |
| --- | --- |
| ![Chat dual](docs/assets/Captura%20desde%202026-01-24%2015-05-28.png) | ![Sidebar mobile](docs/assets/Captura%20desde%202026-01-24%2015-09-50.png) |

![Vista extra](docs/assets/Captura%20desde%202026-01-24%2015-09-57.png)

---

## 🚀 Instalación

### Requisitos previos
- Python 3.10+
- Node.js 18+
- Docker (para PostgreSQL)

### Pasos

```bash
git clone https://github.com/GabrixuGames/ChatME.git
cd ChatME

# Base de datos
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

---

## 🧪 Uso

- Frontend: `http://localhost:8080`
- Backend: `http://localhost:5000`

Flujo basico:
1) Inicia sesion o registrate.
2) Selecciona una sala publica o un amigo.
3) Arrastra una sala o amigo para abrir un chat paralelo.

---

## ⚙️ Configuración

### Backend (`backend/.env`)
- `JWT_SECRET` (min 32 caracteres)
- `FLASK_SECRET_KEY` (min 32 caracteres)
- `ENVIRONMENT` / `FLASK_ENV` (`development` | `production`)
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT`
- `CORS_ALLOWED_ORIGINS` (separado por comas)
- `RATE_LIMITS` (opcional, separado por comas)

### Frontend (`frontend/.env`)
- `VITE_API_URL` (ej: `http://localhost:5000`)
- `VITE_SOCKET_URL` (ej: `http://localhost:5000`)

Documentacion completa:
- `docs/DEVELOPMENT.md`
- `docs/SECURITY.md`
- `docs/CHANGELOG.md`

---

## 🚧 Estado del proyecto

Activo y en evolucion. Refactorizaciones recientes mejoraron la arquitectura, la UI y la documentacion.

---

## 🤝 Contribuir

1) Crea una rama: `feature/nombre`
2) Commits con conventional commits
3) Abre un Pull Request

---

## 📄 Licencia

Sin licencia declarada por ahora.
