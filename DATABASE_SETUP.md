# 🐳 Setup de Base de Datos - ChatApp

## Opción 1: Docker Compose (Recomendado)

### Prerrequisitos
- Docker Desktop instalado
- Git

### Setup rápido
```bash
# 1. Clonar el proyecto
git clone <tu-repo>
cd chatapp-main

# 2. Levantar base de datos
docker-compose up -d

# 3. Verificar que funciona
docker-compose ps
```

### Comandos útiles
```bash
# Ver logs
docker-compose logs postgres

# Parar servicios
docker-compose down

# Reiniciar con datos limpios
docker-compose down -v
docker-compose up -d

# Conectar a PostgreSQL
docker exec -it chatapp-postgres psql -U chatapp -d chatapp
```

## Opción 2: PostgreSQL Local

### Windows
```powershell
# Instalar PostgreSQL
winget install PostgreSQL.PostgreSQL

# Crear base de datos
createdb -U postgres chatapp
psql -U postgres -d chatapp -f database/init.sql
```

### Linux/Mac
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql

# Crear DB
createdb chatapp
psql -d chatapp -f database/init.sql
```

## 🔧 Configuración Backend

Actualizar `backend/app.py`:
```python
# PostgreSQL
db_config = {
    'host': 'localhost',
    'user': 'chatapp',
    'password': 'chatapp123',
    'database': 'chatapp',
    'port': 5432
}
```

## 📊 Datos de Prueba

Usuario por defecto:
- **Username:** testuser
- **Password:** test123

Salas disponibles:
- R1: Sala General
- R2: Sala Desarrollo  
- R3: Sala Random

## 🚀 Migración desde MySQL

Si tienes datos en MySQL:
```bash
# Exportar datos MySQL
mysqldump -u root -p chatapp > chatapp_backup.sql

# Convertir a PostgreSQL (manual o con herramientas)
# Importar a PostgreSQL
psql -U chatapp -d chatapp -f chatapp_converted.sql
```