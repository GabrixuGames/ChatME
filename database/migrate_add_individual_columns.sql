-- Migration: Add columns for individual/private chat rooms
ALTER TABLE rooms
  ADD COLUMN IF NOT EXISTS user_id_1 UUID REFERENCES users(id),
  ADD COLUMN IF NOT EXISTS user_id_2 UUID REFERENCES users(id);

-- Opcional: Actualizar room_type y is_temporary si es necesario
-- UPDATE rooms SET room_type = 'public' WHERE room_type IS NULL;
-- UPDATE rooms SET is_temporary = false WHERE is_temporary IS NULL;

-- Verificar resultado
-- \d rooms
