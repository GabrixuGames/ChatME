-- ChatApp Database Schema
-- PostgreSQL Version

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table with improved security
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    profile_data JSONB DEFAULT '{}'
);

-- Rooms table
CREATE TABLE IF NOT EXISTS rooms (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    room_config JSONB DEFAULT '{}'
);

-- Messages table optimized
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    room_id VARCHAR(50) NOT NULL REFERENCES rooms(id),
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    edited_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_messages_room_created ON messages(room_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Insert default rooms
INSERT INTO rooms (id, name, description, created_at) VALUES 
    ('R1', 'Sala General', 'Canal principal de conversación', NOW()),
    ('R2', 'Sala Desarrollo', 'Para hablar de código y proyectos', NOW()),
    ('R3', 'Sala Random', 'Conversaciones casuales', NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert test user (password: "test123" - recuerda cambiar en producción)
INSERT INTO users (username, email, password_hash) VALUES 
    ('testuser', 'test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LjdOg5J6jKx.vN8zG')
ON CONFLICT (username) DO NOTHING;

-- Views útiles
CREATE OR REPLACE VIEW recent_messages AS
SELECT 
    m.id,
    m.content,
    m.created_at,
    u.username,
    r.name as room_name,
    m.room_id
FROM messages m
JOIN users u ON m.user_id = u.id
JOIN rooms r ON m.room_id = r.id
WHERE m.is_deleted = false
ORDER BY m.created_at DESC;
