"""
Base Repository Class
Implementa el patrón Repository para abstracción de acceso a datos
"""
from abc import ABC
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
            try:
                cursor.execute(query, params)

                # Siempre hacer commit para operaciones de escritura (INSERT, UPDATE, DELETE)
                if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                    connection.commit()

                if fetch_one:
                    result = cursor.fetchone()
                elif fetch_all:
                    result = cursor.fetchall()
                else:
                    result = cursor.rowcount

                logger.debug(f"✅ Query executed successfully: {query[:50]}...")
                return result
            finally:
                cursor.close()
            
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
    
    def update_user_password(self, user_id: str, password_hash: str) -> bool:
        """
        Actualizar password de usuario
        
        Args:
            user_id: ID del usuario
            password_hash: Nuevo hash del password
            
        Returns:
            True si se actualizó correctamente, False si no
        """
        query = "UPDATE users SET password_hash = %s WHERE id = %s"
        try:
            self.execute_query(query, (password_hash, user_id))
            return True
        except Exception as e:
            logger.error(f"Error updating password for user {user_id}: {e}")
            return False
    
    def get_all_users(self) -> List[Dict]:
        """
        Obtener todos los usuarios activos
        
        Returns:
            Lista de usuarios activos
        """
        query = """
            SELECT id, username, email, password_hash, last_login, created_at 
            FROM users 
            WHERE is_active = true 
            ORDER BY created_at
        """
        return self.execute_query(query, fetch_all=True)

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

class RoomRepository(BaseRepository):
    """
    Repository para operaciones de salas
    """
    def get_rooms_for_user(self, user_id):
        """
        Devuelve todas las salas (rooms) en las que el usuario participa, públicas e individuales.
        Incluye filtro de visibilidad para chats individuales.
        """
        query = '''
            SELECT r.* FROM rooms r
            WHERE r.is_active = true
            AND (
                r.room_type = 'public'
                OR (
                    (r.user_id_1 = %s OR r.user_id_2 = %s)
                    AND NOT EXISTS (
                        SELECT 1 FROM user_room_visibility urv
                        WHERE urv.room_id = r.id 
                        AND urv.user_id = %s 
                        AND urv.is_hidden = true
                    )
                )
            )
            ORDER BY r.created_at DESC
        '''
        return self.execute_query(query, (user_id, user_id, user_id), fetch_all=True) or []
    
    def get_all_active_rooms(self) -> List[Dict]:
        """Obtener todas las salas activas"""
        query = "SELECT * FROM rooms WHERE is_active = true ORDER BY created_at"
        return self.execute_query(query, fetch_all=True) or []
    
    def find_by_id(self, room_id: str) -> Optional[Dict]:
        """Buscar sala por ID"""
        query = "SELECT * FROM rooms WHERE id = %s AND is_active = true"
        return self.execute_query(query, (room_id,), fetch_one=True)

    def find_individual_room(self, user_id_1: str, user_id_2: str) -> Optional[Dict]:
        """Buscar sala individual entre dos usuarios (no importa el orden)"""
        query = """
            SELECT * FROM rooms
            WHERE room_type = 'individual'
              AND is_active = true
              AND ((user_id_1 = %s AND user_id_2 = %s) OR (user_id_1 = %s AND user_id_2 = %s))
            LIMIT 1
        """
        return self.execute_query(query, (user_id_1, user_id_2, user_id_2, user_id_1), fetch_one=True)

    def create_individual_room(self, user_id_1: str, user_id_2: str, is_temporary: bool = False, username_1: str = None, username_2: str = None) -> Optional[str]:
        """Crear sala individual entre dos usuarios"""
        import uuid
        query = """
            INSERT INTO rooms (id, name, description, room_type, is_temporary, is_active, user_id_1, user_id_2)
            VALUES (%s, %s, %s, 'individual', %s, true, %s, %s)
            RETURNING id
        """
        room_id = str(uuid.uuid4())
        # Usar username del otro usuario como nombre de sala
        if username_1 and username_2:
            # El nombre será diferente según quién consulte (se formatea en frontend)
            name = f"{username_1} ↔ {username_2}"
        else:
            name = f"Chat privado"
        description = "Chat individual"
        try:
            result = self.execute_query(query, (room_id, name, description, is_temporary, user_id_1, user_id_2), fetch_one=True)
            return result['id'] if result else None
        except Exception as e:
            logger.error(f"❌ Error creando sala individual: {e}")
            return None

    def delete_room(self, room_id: str) -> bool:
        """Eliminar (desactivar) una sala"""
        query = "UPDATE rooms SET is_active = false WHERE id = %s"
        affected_rows = self.execute_query(query, (room_id,))
        return affected_rows > 0
