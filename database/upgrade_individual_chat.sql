-- UPGRADE: Sistema de Chat Individual 1v1
-- Ejecutar después de init.sql

-- PASO 1: Eliminar tablas legacy (sistema duplicado)
DROP TABLE IF EXISTS private_messages CASCADE;
DROP TABLE IF EXISTS private_chats CASCADE;

-- PASO 2: Asegurar que la extensión UUID está activa
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- PASO 3: Agregar índices de performance para chats individuales
CREATE INDEX IF NOT EXISTS idx_rooms_user_participants 
ON rooms(user_id_1, user_id_2) WHERE room_type = 'individual';

CREATE INDEX IF NOT EXISTS idx_messages_room_created_desc 
ON messages(room_id, created_at DESC);

-- PASO 4: Tabla para tracking de mensajes leídos
CREATE TABLE IF NOT EXISTS message_reads (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    read_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, message_id)
);

CREATE INDEX IF NOT EXISTS idx_message_reads_user ON message_reads(user_id);
CREATE INDEX IF NOT EXISTS idx_message_reads_message ON message_reads(message_id);

-- PASO 5: Tabla para visibilidad y estado de salas por usuario
CREATE TABLE IF NOT EXISTS user_room_visibility (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    room_id VARCHAR(50) NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    is_hidden BOOLEAN DEFAULT FALSE,
    last_read_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, room_id)
);

CREATE INDEX IF NOT EXISTS idx_user_room_visibility_user ON user_room_visibility(user_id);
CREATE INDEX IF NOT EXISTS idx_user_room_visibility_room ON user_room_visibility(room_id);

-- PASO 6: Vista para obtener información completa de salas con mensajes no leídos
CREATE OR REPLACE VIEW room_info_view AS
SELECT 
    r.id,
    r.name,
    r.description,
    r.room_type,
    r.is_temporary,
    r.user_id_1,
    r.user_id_2,
    r.created_at,
    (SELECT content FROM messages WHERE room_id = r.id AND is_deleted = false ORDER BY created_at DESC LIMIT 1) as last_message,
    (SELECT created_at FROM messages WHERE room_id = r.id AND is_deleted = false ORDER BY created_at DESC LIMIT 1) as last_message_at,
    (SELECT username FROM messages m JOIN users u ON m.user_id = u.id WHERE m.room_id = r.id AND m.is_deleted = false ORDER BY m.created_at DESC LIMIT 1) as last_message_username
FROM rooms r
WHERE r.is_active = true;

COMMENT ON TABLE message_reads IS 'Tracking de mensajes leídos por usuario';
COMMENT ON TABLE user_room_visibility IS 'Gestión de visibilidad de salas y última lectura por usuario';
COMMENT ON VIEW room_info_view IS 'Vista optimizada con información completa de salas incluyendo último mensaje';
