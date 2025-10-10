# Setup script para ChatApp con PostgreSQL (Windows)

Write-Host "🚀 Configurando ChatApp con PostgreSQL..." -ForegroundColor Green

# Verificar que Docker esté corriendo
try {
    docker info | Out-Null
    Write-Host "✅ Docker está corriendo" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker no está corriendo. Por favor, inicia Docker Desktop primero." -ForegroundColor Red
    exit 1
}

# Crear directorio de base de datos si no existe
if (!(Test-Path "database")) {
    New-Item -ItemType Directory -Path "database"
}

# Levantar PostgreSQL
Write-Host "📦 Descargando y levantando PostgreSQL..." -ForegroundColor Cyan
docker-compose up -d postgres

# Esperar a que PostgreSQL esté listo
Write-Host "⏳ Esperando a que PostgreSQL esté listo..." -ForegroundColor Yellow
do {
    Start-Sleep -Seconds 2
    $result = docker exec chatapp-postgres pg_isready -U chatapp -d chatapp 2>$null
} while ($LASTEXITCODE -ne 0)

Write-Host "✅ PostgreSQL está listo!" -ForegroundColor Green

# Mostrar información de conexión
Write-Host ""
Write-Host "🎉 ¡Setup completado!" -ForegroundColor Green
Write-Host "📊 Información de conexión:" -ForegroundColor Cyan
Write-Host "   Host: localhost"
Write-Host "   Puerto: 5432"
Write-Host "   Base de datos: chatapp"
Write-Host "   Usuario: chatapp"
Write-Host "   Contraseña: chatapp123"
Write-Host ""
Write-Host "🔧 Comandos útiles:" -ForegroundColor Cyan
Write-Host "   Parar:      docker-compose down"
Write-Host "   Ver logs:   docker-compose logs postgres"
Write-Host "   Conectar:   docker exec -it chatapp-postgres psql -U chatapp -d chatapp"
Write-Host ""
Write-Host "🚀 Ahora puedes levantar tu backend con la nueva configuración!" -ForegroundColor Green