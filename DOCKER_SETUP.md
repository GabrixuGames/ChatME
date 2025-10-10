# 🐳 ChatApp con Docker + PostgreSQL - Guía de Setup

## ✅ Cuando Docker termine de instalarse:

### 1. Abrir PowerShell en la carpeta del proyecto
```powershell
cd "C:\Users\Gabrixu\Documents\Programacion\chatapp-main"
```

### 2. Levantar PostgreSQL (un solo comando)
```powershell
# Opción A: Script automático
.\setup-db.ps1

# Opción B: Manual
docker-compose up -d postgres
```

### 3. Instalar dependencias del backend
```powershell
cd backend
pip install -r requirements.txt
```

### 4. Levantar el backend
```powershell
python app.py
```

### 5. Levantar el frontend (en otra terminal)
```powershell
cd ..\frontend
npm install
npm run dev
```

## 🎯 ¿Todo funcionando?

Deberías ver:
- ✅ PostgreSQL: `http://localhost:5432`
- ✅ Backend: `http://localhost:5000`  
- ✅ Frontend: `http://localhost:8080`

## 🔧 Comandos útiles Docker:

```powershell
# Ver contenedores corriendo
docker ps

# Ver logs de PostgreSQL
docker-compose logs postgres

# Parar todo
docker-compose down

# Conectar a la base de datos
docker exec -it chatapp-postgres psql -U chatapp -d chatapp
```

## 🚨 Si algo falla:

1. **Docker no inicia:** Reinicia Docker Desktop
2. **Puerto ocupado:** Cambia puertos en docker-compose.yml
3. **Dependencias Python:** Usa un virtual environment
4. **PostgreSQL no conecta:** Espera 30 segundos más

## 📊 Datos de prueba ya incluidos:

- **Usuario:** testuser
- **Contraseña:** test123
- **Salas:** R1, R2, R3

¡Listo para chatear! 🚀