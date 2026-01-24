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

    def get_room_by_id(self, room_id: str) -> Optional[Dict]:
        """Obtener sala por ID"""
        return self.room_repository.find_by_id(room_id)
    
    def get_user_rooms_detailed(self, user_id: str, username: str):
        """
        Devuelve salas con información completa: último mensaje, contador no leídos, nombre personalizado
        Optimizado: Una sola query con subqueries en lugar de N+1 queries
        """
        # Query optimizada con subqueries laterales
        optimized_query = """
            SELECT
                r.*,
                -- Otro usuario para chats individuales
                CASE
                    WHEN r.room_type = 'individual' AND r.user_id_1 = %s THEN u2.username
                    WHEN r.room_type = 'individual' AND r.user_id_2 = %s THEN u1.username
                    ELSE NULL
                END as other_username,
                CASE
                    WHEN r.room_type = 'individual' AND r.user_id_1 = %s THEN r.user_id_2::text
                    WHEN r.room_type = 'individual' AND r.user_id_2 = %s THEN r.user_id_1::text
                    ELSE NULL
                END as other_user_id,
                -- Último mensaje
                lm.content as last_message,
                lm.created_at as last_message_at,
                lm.sender_username as last_message_username,
                -- Conteo no leídos
                COALESCE(unread.count, 0) as unread_count
            FROM rooms r
            LEFT JOIN users u1 ON r.user_id_1 = u1.id
            LEFT JOIN users u2 ON r.user_id_2 = u2.id
            -- Último mensaje (subquery lateral)
            LEFT JOIN LATERAL (
                SELECT m.content, m.created_at, u.username as sender_username
                FROM messages m
                JOIN users u ON m.user_id = u.id
                WHERE m.room_id = r.id AND m.is_deleted = false
                ORDER BY m.created_at DESC
                LIMIT 1
            ) lm ON true
            -- Conteo no leídos (subquery)
            LEFT JOIN LATERAL (
                SELECT COUNT(*) as count
                FROM messages m
                WHERE m.room_id = r.id
                AND m.is_deleted = false
                AND m.user_id != %s
                AND NOT EXISTS (
                    SELECT 1 FROM message_reads mr
                    WHERE mr.message_id = m.id AND mr.user_id = %s
                )
            ) unread ON true
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
            ORDER BY lm.created_at DESC NULLS LAST
        """

        try:
            rooms = self.room_repository.execute_query(
                optimized_query,
                (user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id),
                fetch_all=True
            )

            detailed_rooms = []
            for room in (rooms or []):
                room_detail = dict(room)

                # Para chats individuales, usar el nombre del otro usuario
                if room.get('room_type') == 'individual' and room.get('other_username'):
                    room_detail['name'] = room['other_username']

                # Formatear fecha del último mensaje
                if room_detail.get('last_message_at'):
                    room_detail['last_message_at'] = room_detail['last_message_at'].isoformat()

                detailed_rooms.append(room_detail)

            logger.info(f"📚 Obtenidos {len(detailed_rooms)} rooms detallados para usuario {user_id}")
            return detailed_rooms

        except Exception as e:
            logger.error(f"❌ Error en get_user_rooms_detailed: {e}")
            # Fallback al método anterior si hay error
            return self._get_user_rooms_detailed_fallback(user_id, username)

    def _get_user_rooms_detailed_fallback(self, user_id: str, username: str):
        """Método fallback para obtener rooms (N+1 queries, menos eficiente)"""
        rooms = self.room_repository.get_rooms_for_user(user_id)
        detailed_rooms = []

        for room in rooms:
            room_detail = dict(room)

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

            unread_count = self.get_unread_count(user_id, room['id'])
            room_detail['unread_count'] = unread_count
            detailed_rooms.append(room_detail)

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
            # Si el room existe pero estaba oculto para el usuario, mostrarlo
            self.show_room(str(user1['id']), room['id'])
            return room
        room_id = self.room_repository.create_individual_room(
            str(user1['id']), str(user2['id']), is_temporary, username_1=username_1, username_2=username_2
        )
        if room_id:
            return self.room_repository.find_by_id(room_id)
        return None

    def show_room(self, user_id: str, room_id: str) -> bool:
        """
        Mostrar sala para un usuario (quitar de ocultos)
        """
        query = """
            UPDATE user_room_visibility
            SET is_hidden = false
            WHERE user_id = %s AND room_id = %s
        """
        affected = self.room_repository.execute_query(query, (user_id, room_id))
        if affected and affected > 0:
            logger.info(f"👁️ Sala {room_id} mostrada para usuario {user_id}")
        return affected > 0 if affected else False

    def is_user_in_room(self, user_id: str, room_id: str) -> bool:
        """
        Verificar si un usuario es parte de un room (autorización)
        """
        query = """
            SELECT 1 FROM rooms
            WHERE id = %s AND is_active = true
            AND (
                room_type = 'public'
                OR user_id_1 = %s
                OR user_id_2 = %s
            )
            LIMIT 1
        """
        result = self.room_repository.execute_query(
            query, (room_id, user_id, user_id), fetch_one=True
        )
        return result is not None

    def get_visible_users_count(self, room_id: str) -> int:
        """
        Contar usuarios que tienen el room visible (no oculto)
        """
        query = """
            SELECT
                CASE
                    WHEN r.room_type != 'individual' THEN 1
                    ELSE (
                        SELECT COUNT(*)
                        FROM (VALUES (r.user_id_1), (r.user_id_2)) AS participants(user_id)
                        WHERE participants.user_id IS NOT NULL
                          AND NOT EXISTS (
                              SELECT 1 FROM user_room_visibility urv
                              WHERE urv.room_id = r.id
                                AND urv.user_id = participants.user_id
                                AND urv.is_hidden = true
                          )
                    )
                END AS count
            FROM rooms r
            WHERE r.id = %s
        """
        result = self.room_repository.execute_query(query, (room_id,), fetch_one=True)
        return result['count'] if result and result['count'] is not None else 0

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
            # Validar contenido primero (evitar DB calls innecesarias)
            if not content or not content.strip():
                logger.warning("📝 Contenido de mensaje vacío")
                return None

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
    
    def delete_room_permanently(self, room_id: str) -> bool:
        """
        Eliminar permanentemente un room y todos sus datos asociados
        Se usa cuando ambos usuarios han ocultado el chat
        """
        connection = None
        try:
            connection = self.room_repository.db_manager.get_connection()
            with connection.cursor() as cursor:
                # Primero, obtener los user_ids del room antes de eliminarlo (si es individual)
                cursor.execute("""
                    SELECT user_id_1, user_id_2 FROM rooms 
                    WHERE id = %s AND room_type = 'individual'
                """, (room_id,))
                room_users = cursor.fetchone()

                # 1. Eliminar mensajes del room
                cursor.execute("DELETE FROM messages WHERE room_id = %s", (room_id,))
                messages_deleted = cursor.rowcount

                # 2. Eliminar visibilidad del room
                cursor.execute("DELETE FROM user_room_visibility WHERE room_id = %s", (room_id,))
                visibility_deleted = cursor.rowcount

                # 3. Eliminar el room
                cursor.execute("DELETE FROM rooms WHERE id = %s", (room_id,))

                # 4. (Opcional) Eliminar amistades inactivas asociadas si era chat individual
                if room_users:
                    user_id_1, user_id_2 = room_users
                    cursor.execute("""
                        DELETE FROM friendships
                        WHERE status = 'inactive'
                        AND user_id_1 = LEAST(%s, %s)
                        AND user_id_2 = GREATEST(%s, %s)
                    """, (user_id_1, user_id_2, user_id_1, user_id_2))
            
            connection.commit()
            self.room_repository.db_manager.return_connection(connection)
            
            logger.info(f"🗑️ Room {room_id} eliminado permanentemente: {messages_deleted} mensajes, {visibility_deleted} visibilidades")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error eliminando room {room_id}: {e}")
            if connection:
                connection.rollback()
                self.room_repository.db_manager.return_connection(connection)
            return False
