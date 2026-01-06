"""
Chat Service
Maneja toda la lógica de negocio relacionada con mensajes y salas
"""
from typing import List, Dict, Optional
from repositories.base_repository import MessageRepository, RoomRepository, UserRepository
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatService:
    """
    Servicio de chat
    Encapsula la lógica de negocio para mensajes, salas, etc.
    """
    
    def __init__(self):
        self.message_repository = MessageRepository()
        self.room_repository = RoomRepository()
        self.user_repository = UserRepository()
    
    def get_user_rooms(self, user_id):
        """
        Devuelve todas las salas (rooms) en las que el usuario participa, públicas e individuales.
        """
        return self.room_repository.get_rooms_for_user(user_id)
    
    def get_user_rooms_detailed(self, user_id: str, username: str):
        """
        Devuelve salas con información completa: último mensaje, contador no leídos, nombre personalizado
        """
        rooms = self.room_repository.get_rooms_for_user(user_id)
        detailed_rooms = []
        
        for room in rooms:
            room_detail = dict(room)
            
            # Para chats individuales, personalizar el nombre
            if room.get('room_type') == 'individual':
                user_id_1 = room.get('user_id_1')
                user_id_2 = room.get('user_id_2')
                other_user_id = user_id_2 if str(user_id_1) == str(user_id) else user_id_1
                
                if other_user_id:
                    other_user = self.user_repository.find_by_id(str(other_user_id))
                    if other_user:
                        room_detail['name'] = other_user['username']
                        room_detail['other_username'] = other_user['username']
                        room_detail['other_user_id'] = str(other_user_id)
            
            # Obtener último mensaje
            last_message_query = """
                SELECT m.content, m.created_at, u.username
                FROM messages m
                JOIN users u ON m.user_id = u.id
                WHERE m.room_id = %s AND m.is_deleted = false
                ORDER BY m.created_at DESC
                LIMIT 1
            """
            last_msg = self.message_repository.execute_query(
                last_message_query, (room['id'],), fetch_one=True
            )
            
            if last_msg:
                room_detail['last_message'] = last_msg['content']
                room_detail['last_message_at'] = last_msg['created_at'].isoformat() if last_msg['created_at'] else None
                room_detail['last_message_username'] = last_msg['username']
            
            # Obtener mensajes no leídos
            unread_count = self.get_unread_count(user_id, room['id'])
            room_detail['unread_count'] = unread_count
            
            detailed_rooms.append(room_detail)
        
        # Ordenar por último mensaje (más reciente primero)
        detailed_rooms.sort(key=lambda x: x.get('last_message_at') or '', reverse=True)
        return detailed_rooms
    
    def get_unread_count(self, user_id: str, room_id: str) -> int:
        """
        Contar mensajes no leídos en una sala
        """
        query = """
            SELECT COUNT(*) as count
            FROM messages m
            WHERE m.room_id = %s 
              AND m.is_deleted = false
              AND m.user_id != %s
              AND NOT EXISTS (
                  SELECT 1 FROM message_reads mr 
                  WHERE mr.message_id = m.id AND mr.user_id = %s
              )
        """
        result = self.message_repository.execute_query(
            query, (room_id, user_id, user_id), fetch_one=True
        )
        return result['count'] if result else 0
    
    def mark_messages_as_read(self, user_id: str, room_id: str) -> int:
        """
        Marcar todos los mensajes de una sala como leídos
        """
        query = """
            INSERT INTO message_reads (user_id, message_id)
            SELECT %s, m.id
            FROM messages m
            WHERE m.room_id = %s 
              AND m.is_deleted = false
              AND m.user_id != %s
              AND NOT EXISTS (
                  SELECT 1 FROM message_reads mr 
                  WHERE mr.message_id = m.id AND mr.user_id = %s
              )
            ON CONFLICT DO NOTHING
        """
        affected = self.message_repository.execute_query(
            query, (user_id, room_id, user_id, user_id)
        )
        return affected if affected else 0
    
    def hide_room(self, user_id: str, room_id: str) -> bool:
        """
        Ocultar sala para un usuario
        """
        query = """
            INSERT INTO user_room_visibility (user_id, room_id, is_hidden)
            VALUES (%s, %s, true)
            ON CONFLICT (user_id, room_id) 
            DO UPDATE SET is_hidden = true
        """
        affected = self.room_repository.execute_query(query, (user_id, room_id))
        return affected > 0

    def get_or_create_individual_room(self, username_1: str, username_2: str, is_temporary: bool = False) -> Optional[Dict]:
        """Busca o crea una sala individual entre dos usuarios"""
        user1 = self.user_repository.find_by_username(username_1)
        user2 = self.user_repository.find_by_username(username_2)
        if not user1 or not user2:
            logger.warning(f"👤 Usuarios no encontrados: {username_1}, {username_2}")
            return None
        room = self.room_repository.find_individual_room(str(user1['id']), str(user2['id']))
        if room:
            return room
        room_id = self.room_repository.create_individual_room(
            str(user1['id']), str(user2['id']), is_temporary, username_1=username_1, username_2=username_2
        )
        if room_id:
            return self.room_repository.find_by_id(room_id)
        return None

    def delete_room(self, room_id: str) -> bool:
        """Eliminar/desactivar una sala"""
        return self.room_repository.delete_room(room_id)

    def cleanup_temporary_rooms(self, user_id: str) -> int:
        """Desactiva todos los chats temporales donde participa el usuario"""
        query = """
            UPDATE rooms SET is_active = false
            WHERE is_temporary = true AND is_active = true
              AND (user_id_1 = %s OR user_id_2 = %s)
        """
        affected_rows = self.room_repository.execute_query(query, (user_id, user_id))
        return affected_rows if affected_rows else 0
    
    def send_message(self, username: str, room_id: str, content: str) -> Optional[Dict]:
        """
        Enviar un mensaje a una sala
        
        Args:
            username: Username del remitente
            room_id: ID de la sala
            content: Contenido del mensaje
            
        Returns:
            Dict con información del mensaje enviado o None si hay error
        """
        try:
            # Validar que la sala existe
            room = self.room_repository.find_by_id(room_id)
            if not room:
                logger.warning(f"🏠 Sala no encontrada: {room_id}")
                return None
            
            # Obtener usuario
            user = self.user_repository.find_by_username(username)
            if not user:
                logger.warning(f"👤 Usuario no encontrado: {username}")
                return None
            
            # Validar contenido
            if not content or not content.strip():
                logger.warning("📝 Contenido de mensaje vacío")
                return None
            
            # Sanitizar contenido (remover caracteres peligrosos)
            sanitized_content = self._sanitize_message_content(content.strip())
            
            # Guardar mensaje
            message_id = self.message_repository.save_message(
                user_id=str(user['id']),
                room_id=room_id,
                content=sanitized_content
            )
            
            if not message_id:
                logger.error("❌ Error guardando mensaje en base de datos")
                return None
            
            logger.info(f"📨 Mensaje enviado: {username} -> {room_id}")
            
            # Retornar información del mensaje
            return {
                "id": message_id,
                "username": username,
                "content": sanitized_content,
                "timestamp": datetime.now().isoformat(),
                "roomId": room_id,
                "room": room_id,  # Compatibilidad
                "userId": str(user['id'])
            }
            
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje: {e}")
            return None
    
    def get_room_messages(self, room_id: str, page: int = 1, per_page: int = 50) -> List[Dict]:
        """
        Obtener mensajes de una sala con paginación
        
        Args:
            room_id: ID de la sala
            page: Número de página (empezando en 1)
            per_page: Mensajes por página
            
        Returns:
            Lista de mensajes en formato frontend
        """
        try:
            # Validar parámetros
            if page < 1:
                page = 1
            if per_page < 1 or per_page > 100:
                per_page = 50
            
            offset = (page - 1) * per_page
            
            # Obtener mensajes
            messages = self.message_repository.get_messages_by_room(
                room_id=room_id,
                limit=per_page,
                offset=offset
            )
            
            # Convertir a formato frontend
            result = []
            for msg in messages:
                result.append({
                    'id': str(msg['id']),
                    'roomId': msg['room_id'],
                    'room': msg['room_id'],  # Por compatibilidad
                    'username': msg['username'],
                    'userId': msg['username'],  # Por compatibilidad
                    'content': msg['content'],
                    'timestamp': msg['created_at'].isoformat()
                })
            
            logger.info(f"📚 Obtenidos {len(result)} mensajes para sala {room_id} (página {page})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo mensajes: {e}")
            return []
    
    def get_available_rooms(self) -> List[Dict]:
        """
        Obtener todas las salas disponibles
        
        Returns:
            Lista de salas en formato frontend
        """
        try:
            rooms = self.room_repository.get_all_active_rooms()
            
            result = []
            for room in rooms:
                result.append({
                    'id': room['id'],
                    'name': room['name'],
                    'description': room['description']
                })
            
            logger.info(f"🏠 Obtenidas {len(result)} salas disponibles")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo salas: {e}")
            return []
    
    def _sanitize_message_content(self, content: str) -> str:
        """
        Sanitizar contenido de mensajes
        Remover caracteres potencialmente peligrosos
        """
        # Limitar longitud
        if len(content) > 1000:
            content = content[:1000]
        
        # Remover caracteres de control (excepto \n, \r, \t)
        sanitized = ''.join(char for char in content if ord(char) >= 32 or char in '\n\r\t')
        
        return sanitized.strip()
