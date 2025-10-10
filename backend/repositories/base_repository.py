"""
Base Repository Class
Implementa el patrón Repository para abstracción de acceso a datos
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from utils.database import db_manager
import psycopg2.extras
import logging

logger = logging.getLogger(__name__)

class BaseRepository(ABC):
    """
    Clase base para todos los repositorios
    Implementa operaciones CRUD básicas
    """
    
    def __init__(self):
        self.db_manager = db_manager
    
    def execute_query(self, query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False) -> Optional[Any]:
        """
        Ejecutar una query con manejo de conexiones del pool
        
        Args:
            query: SQL query to execute
            params: Parameters for the query
            fetch_one: Return single result
            fetch_all: Return all results
            
        Returns:
            Query result or None
        """
        connection = None
        try:
            connection = self.db_manager.get_connection()
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute(query, params)
            
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                connection.commit()
                result = cursor.rowcount
                
            logger.debug(f"✅ Query executed successfully: {query[:50]}...")
            return result
            
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"❌ Error executing query: {e}")
            logger.error(f"Query: {query}")
            raise
            
        finally:
            if connection:
                self.db_manager.return_connection(connection)

class UserRepository(BaseRepository):
    """
    Repository para operaciones de usuarios
    """
    
    def find_by_username(self, username: str) -> Optional[Dict]:
        """Buscar usuario por username"""
        query = "SELECT * FROM users WHERE username = %s AND is_active = true"
        return self.execute_query(query, (username,), fetch_one=True)
    
    def find_by_id(self, user_id: str) -> Optional[Dict]:
        """Buscar usuario por ID"""
        query = "SELECT * FROM users WHERE id = %s AND is_active = true"
        return self.execute_query(query, (user_id,), fetch_one=True)
    
    def create_user(self, username: str, email: str, password_hash: str) -> str:
        """Crear nuevo usuario"""
        query = """
            INSERT INTO users (username, email, password_hash) 
            VALUES (%s, %s, %s) 
            RETURNING id
        """
        result = self.execute_query(query, (username, email, password_hash), fetch_one=True)
        return result['id'] if result else None
    
    def update_last_login(self, user_id: str) -> None:
        """Actualizar último login"""
        query = "UPDATE users SET last_login = NOW() WHERE id = %s"
        self.execute_query(query, (user_id,))

class MessageRepository(BaseRepository):
    """
    Repository para operaciones de mensajes
    """
    
    def save_message(self, user_id: str, room_id: str, content: str) -> Optional[str]:
        """Guardar nuevo mensaje"""
        query = """
            INSERT INTO messages (user_id, room_id, content) 
            VALUES (%s, %s, %s) 
            RETURNING id
        """
        result = self.execute_query(query, (user_id, room_id, content), fetch_one=True)
        return result['id'] if result else None
    
    def get_messages_by_room(self, room_id: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Obtener mensajes de una sala con paginación"""
        query = """
            SELECT m.id, m.content, m.created_at, u.username, m.room_id
            FROM messages m
            JOIN users u ON m.user_id = u.id
            WHERE m.room_id = %s AND m.is_deleted = false
            ORDER BY m.created_at DESC
            LIMIT %s OFFSET %s
        """
        messages = self.execute_query(query, (room_id, limit, offset), fetch_all=True)
        return list(reversed(messages)) if messages else []  # Reverse para orden cronológico
    
    def get_message_count_by_room(self, room_id: str) -> int:
        """Contar mensajes en una sala"""
        query = "SELECT COUNT(*) as count FROM messages WHERE room_id = %s AND is_deleted = false"
        result = self.execute_query(query, (room_id,), fetch_one=True)
        return result['count'] if result else 0
    
    def delete_message(self, message_id: str, user_id: str) -> bool:
        """Soft delete de mensaje (solo el autor puede borrar)"""
        query = """
            UPDATE messages 
            SET is_deleted = true, edited_at = NOW() 
            WHERE id = %s AND user_id = %s
        """
        affected_rows = self.execute_query(query, (message_id, user_id))
        return affected_rows > 0

class RoomRepository(BaseRepository):
    """
    Repository para operaciones de salas
    """
    
    def get_all_active_rooms(self) -> List[Dict]:
        """Obtener todas las salas activas"""
        query = "SELECT * FROM rooms WHERE is_active = true ORDER BY created_at"
        return self.execute_query(query, fetch_all=True) or []
    
    def find_by_id(self, room_id: str) -> Optional[Dict]:
        """Buscar sala por ID"""
        query = "SELECT * FROM rooms WHERE id = %s AND is_active = true"
        return self.execute_query(query, (room_id,), fetch_one=True)