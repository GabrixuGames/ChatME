#!/bin/bash
# Setup script para ChatApp con PostgreSQL

echo "🚀 Configurando ChatApp con PostgreSQL..."

# Cargar variables de entorno si existe .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Verificar que Docker esté corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Por favor, inicia Docker Desktop primero."
    exit 1
fi

echo "✅ Docker está corriendo"

# Crear directorio de base de datos si no existe
mkdir -p database

# Levantar PostgreSQL y Redis
echo "📦 Descargando y levantando servicios..."
docker-compose up -d postgres redis

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a que PostgreSQL esté listo..."
until docker exec chatapp-postgres pg_isready -U ${DB_USER:-chatapp} -d ${DB_NAME:-chatapp}; do
  echo "Esperando PostgreSQL..."
  sleep 2
done

echo "✅ PostgreSQL está listo!"

# Mostrar información de conexión
echo ""
echo "🎉 ¡Setup completado!"
echo "📊 Información de conexión:"
echo "   Host: ${DB_HOST:-localhost}"
echo "   Puerto: ${DB_PORT:-5432}"
echo "   Base de datos: ${DB_NAME:-chatapp}"
echo "   Usuario: ${DB_USER:-chatapp}"
echo "   Contraseña: ${DB_PASSWORD:-chatapp123}"
echo ""
echo "🔧 Comandos útiles:"
echo "   Parar servicios:    docker-compose down"
echo "   Ver logs:          docker-compose logs"
echo "   Conectar DB:       docker exec -it chatapp-postgres psql -U ${DB_USER:-chatapp} -d ${DB_NAME:-chatapp}"
echo "   Levantar todo:     docker-compose up --build -d"
echo ""
echo "🚀 Ahora puedes usar la aplicación!"