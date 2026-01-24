-- Fix: Aumentar el tamaño de room_id para soportar UUIDs
-- Los chats individuales usan UUIDs (36 caracteres) mientras que las salas públicas usan IDs cortos (R1, R2, etc)

-- 1. Modificar tabla rooms para soportar IDs más largos (UUID o texto corto)
ALTER TABLE rooms ALTER COLUMN id TYPE VARCHAR(50);

-- 2. Modificar tabla messages para reflejar el cambio
ALTER TABLE messages ALTER COLUMN room_id TYPE VARCHAR(50);

-- 3. Si existe la tabla user_room_visibility
ALTER TABLE user_room_visibility ALTER COLUMN room_id TYPE VARCHAR(50);

-- Verificar cambios
SELECT 
    table_name,
    column_name, 
    data_type,
    character_maximum_length
FROM information_schema.columns 
WHERE column_name = 'room_id' OR (column_name = 'id' AND table_name = 'rooms')
ORDER BY table_name, column_name;
