-- Complete migration for friend system and missing columns

-- Add room_type column to rooms table
ALTER TABLE rooms
  ADD COLUMN IF NOT EXISTS room_type VARCHAR(20) DEFAULT 'public',
  ADD COLUMN IF NOT EXISTS is_temporary BOOLEAN DEFAULT false;

-- Create friend_requests table
CREATE TABLE IF NOT EXISTS friend_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    receiver_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected', 'cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(sender_id, receiver_id)
);

-- Create friendships table
CREATE TABLE IF NOT EXISTS friendships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id_1 UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_id_2 UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'blocked')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id_1, user_id_2),
    CHECK (user_id_1 < user_id_2)
);

-- Create friends_list view
CREATE OR REPLACE VIEW friends_list AS
SELECT 
    f.id,
    f.user_id_1,
    f.user_id_2,
    f.status,
    f.created_at,
    u1.username as username_1,
    u2.username as username_2
FROM friendships f
JOIN users u1 ON f.user_id_1 = u1.id
JOIN users u2 ON f.user_id_2 = u2.id
WHERE f.status = 'active';

-- Create user_room_visibility table for hiding rooms
CREATE TABLE IF NOT EXISTS user_room_visibility (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    room_id VARCHAR(50) NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    is_hidden BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, room_id)
);

-- Add profile_pic column to users if not exists
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS profile_pic TEXT;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_friend_requests_sender ON friend_requests(sender_id);
CREATE INDEX IF NOT EXISTS idx_friend_requests_receiver ON friend_requests(receiver_id);
CREATE INDEX IF NOT EXISTS idx_friend_requests_status ON friend_requests(status);
CREATE INDEX IF NOT EXISTS idx_friendships_user1 ON friendships(user_id_1);
CREATE INDEX IF NOT EXISTS idx_friendships_user2 ON friendships(user_id_2);
CREATE INDEX IF NOT EXISTS idx_friendships_status ON friendships(status);
CREATE INDEX IF NOT EXISTS idx_user_room_visibility ON user_room_visibility(user_id, room_id);

-- Update existing rooms to have public type
UPDATE rooms SET room_type = 'public' WHERE room_type IS NULL;
UPDATE rooms SET is_temporary = false WHERE is_temporary IS NULL;
