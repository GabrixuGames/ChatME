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
            
            # Retornar formato consistente para el frontend
            return {
                'id': str(message_id),
                'roomId': room_id,
                'room': room_id,  # Por compatibilidad
                'username': username,
                'userId': username,  # Por compatibilidad
                'content': sanitized_content,
                'timestamp': datetime.now().isoformat()
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