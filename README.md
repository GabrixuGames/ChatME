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

### Desarrollo Local

#### Requisitos previos
- Python 3.10+
- Node.js 18+
- Docker (para PostgreSQL)

#### Pasos

```bash
git clone https://github.com/GabrixuGames/ChatME.git
cd ChatME

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores seguros

# Base de datos
docker-compose up -d postgres redis

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py

# Frontend (en otra terminal)
cd ../frontend
npm install
npm run dev
```

### Producción con Docker

```bash
git clone https://github.com/GabrixuGames/ChatME.git
cd ChatME

# Configurar variables de entorno
cp .env.example .env
# Editar .env con valores de producción

# Construir y levantar todos los servicios
docker-compose up --build -d

# Acceder a la aplicación en http://localhost
```

#### Servicios incluidos:
- **PostgreSQL**: Base de datos
- **Redis**: Cache y sesiones
- **Backend**: API Flask
- **Frontend**: Aplicación React
- **Nginx**: Reverse proxy

---

## 🧪 Uso

### Desarrollo Local
- Frontend: `http://localhost:8080`
- Backend: `http://localhost:5000`

### Producción
- Aplicación completa: `http://localhost` (puerto 80)
- API directa: `http://localhost/api`

Flujo basico:
1) Inicia sesion o registrate.
2) Selecciona una sala publica o un amigo.
3) Arrastra una sala o amigo para abrir un chat paralelo.

---

## ⚙️ Configuración

### Variables de Entorno (.env)

#### Backend
- `JWT_SECRET` (min 32 caracteres)
- `FLASK_SECRET_KEY` (min 32 caracteres)
- `FLASK_ENV` (`development` | `production`)
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT`
- `CORS_ORIGINS` (URLs permitidas, separado por comas)
- `REDIS_URL` (opcional, para cache)

#### Frontend
- `VITE_API_URL` (ej: `http://localhost/api` para prod, `http://localhost:5000` para dev)
- `VITE_SOCKET_URL` (ej: `http://localhost` para prod, `http://localhost:5000` para dev)

### Producción Adicional
- Configurar SSL en nginx para HTTPS
- Usar secrets de Docker en lugar de variables de entorno para passwords
- Configurar logging y monitoreo
- Backup de base de datos

## 🚀 Deployment

### Con Docker Compose (Recomendado)
1. Configurar `.env` con valores de producción
2. Ejecutar `docker-compose up --build -d`
3. La aplicación estará disponible en `http://your-domain`

### Configuración SSL
Para HTTPS, actualizar `nginx.conf` y agregar certificados SSL en `./ssl/`

### Escalado
- Usar Docker Swarm o Kubernetes para múltiples instancias
- Configurar load balancer para backend
- Usar Redis Cluster para alta disponibilidad

Documentacion completa:
- `docs/DEVELOPMENT.md`
- `docs/SECURITY.md`
- `docs/CHANGELOG.md`

---

## 🚧 Estado del proyecto

Activo y en evolucion. Refactorizaciones recientes mejoraron la arquitectura, la UI y la documentacion.

---
