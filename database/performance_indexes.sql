-- Performance Optimization Indexes
-- Índices adicionales para mejorar el rendimiento de queries frecuentes

-- Índice compuesto para la query principal de mensajes
-- Optimiza: WHERE room_id = ? AND is_deleted = false ORDER BY created_at DESC
CREATE INDEX IF NOT EXISTS idx_messages_room_active_created 
ON messages(room_id, is_deleted, created_at DESC);

-- Índice para búsquedas por usuario y sala
CREATE INDEX IF NOT EXISTS idx_messages_user_room 
ON messages(user_id, room_id) 
WHERE is_deleted = false;

-- Índice para mensajes recientes (útil para paginación)
CREATE INDEX IF NOT EXISTS idx_messages_created_desc 
ON messages(created_at DESC) 
WHERE is_deleted = false;

-- Índice parcial para usuarios activos
CREATE INDEX IF NOT EXISTS idx_users_active_username 
ON users(username) 
WHERE is_active = true;

-- Índice para last_login (útil para estadísticas)
CREATE INDEX IF NOT EXISTS idx_users_last_login 
ON users(last_login DESC) 
WHERE is_active = true;

-- Estadísticas para el optimizador
ANALYZE messages;
ANALYZE users;
ANALYZE rooms;