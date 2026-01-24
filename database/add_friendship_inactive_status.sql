-- Migración: Agregar sistema de amistad inactiva
-- Fecha: 2026-01-06
-- Descripción: Permite marcar amistades como inactivas sin eliminar el historial de chat

-- Agregar campo is_active a friends_list
ALTER TABLE friends_list 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

-- Actualizar registros existentes a activos
UPDATE friends_list SET is_active = true WHERE is_active IS NULL;

-- Crear índice para consultas más rápidas
CREATE INDEX IF NOT EXISTS idx_friends_active ON friends_list(user_id, is_active);

-- Verificación
SELECT 'Migración completada: friends_list ahora tiene campo is_active' AS status;
