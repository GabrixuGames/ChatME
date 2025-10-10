#!/bin/bash
# Setup script para ChatApp con PostgreSQL

echo "🚀 Configurando ChatApp con PostgreSQL..."

# Verificar que Docker esté corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Por favor, inicia Docker Desktop primero."
    exit 1
fi

echo "✅ Docker está corriendo"

# Crear directorio de base de datos si no existe
mkdir -p database

# Levantar PostgreSQL
echo "📦 Descargando y levantando PostgreSQL..."
docker-compose up -d postgres

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a que PostgreSQL esté listo..."
until docker exec chatapp-postgres pg_isready -U chatapp -d chatapp; do
  echo "Esperando PostgreSQL..."
  sleep 2
done

echo "✅ PostgreSQL está listo!"

# Mostrar información de conexión
echo ""
echo "🎉 ¡Setup completado!"
echo "📊 Información de conexión:"
echo "   Host: localhost"
echo "   Puerto: 5432"
echo "   Base de datos: chatapp"
echo "   Usuario: chatapp"
echo "   Contraseña: chatapp123"
echo ""
echo "🔧 Comandos útiles:"
echo "   Parar:      docker-compose down"
echo "   Ver logs:   docker-compose logs postgres"
echo "   Conectar:   docker exec -it chatapp-postgres psql -U chatapp -d chatapp"
echo ""
echo "🚀 Ahora puedes levantar tu backend con la nueva configuración!"