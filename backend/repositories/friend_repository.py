from typing import List, Optional, Dict
from repositories.base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)

class FriendRepository(BaseRepository):
    def remove_friend(self, user_id: str, friend_id: str) -> bool:
        """Marcar amistad como inactiva en lugar de eliminarla"""
        query = '''
            UPDATE friendships 
            SET status = 'inactive'
            WHERE (
                (user_id_1 = %s AND user_id_2 = %s)
                OR (user_id_1 = %s AND user_id_2 = %s)
            )
              AND status = 'active'
        '''
        try:
            self.execute_query(query, (user_id, friend_id, friend_id, user_id))
            logger.info(f"✅ Amistad marcada como inactiva: {user_id} - {friend_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error marcando amistad como inactiva: {e}")
            return False
    
    def __init__(self):
        super().__init__()

    def send_request(self, sender_id: str, receiver_id: str) -> Optional[str]:
        query = '''
            INSERT INTO friend_requests (sender_id, receiver_id)
            VALUES (%s, %s)
            ON CONFLICT (sender_id, receiver_id) DO NOTHING
            RETURNING id
        '''
        try:
            result = self.execute_query(query, (sender_id, receiver_id), fetch_one=True)
            if result:
                logger.info(f"✅ Solicitud de amistad enviada: {sender_id} -> {receiver_id}")
                return result['id']
            else:
                logger.warning(f"⚠️  Ya existe solicitud entre: {sender_id} -> {receiver_id}")
                return None
        except Exception as e:
            logger.error(f"❌ Error enviando solicitud de amistad: {e}")
            return None

    def respond_request(self, request_id: str, status: str) -> bool:
        """Responder solicitud de amistad de forma segura"""
        try:
            # Validar status
            if status not in ['accepted', 'rejected']:
                logger.error(f"❌ Status inválido: {status}")
                return False
            
            # Obtener la solicitud
            get_query = "SELECT sender_id, receiver_id FROM friend_requests WHERE id = %s"
            req = self.execute_query(get_query, (request_id,), fetch_one=True)
            
            if not req:
                logger.warning(f"⚠️  Solicitud no encontrada: {request_id}")
                return False
            
            # Actualizar estado de la solicitud
            update_query = '''
                UPDATE friend_requests SET status = %s, responded_at = NOW()
                WHERE id = %s
            '''
            self.execute_query(update_query, (status, request_id))
            
            # Si se acepta, crear relación en friendships
            if status == 'accepted':
                sender = req['sender_id']
                receiver = req['receiver_id']
                
                # Asegurar orden consistente
                user1 = min(sender, receiver)
                user2 = max(sender, receiver)
                
                insert_query = '''
                    INSERT INTO friendships (user_id_1, user_id_2, status, created_at) 
                    VALUES (%s, %s, 'active', NOW())
                    ON CONFLICT (user_id_1, user_id_2) 
                    DO UPDATE SET status = 'active'
                '''
                self.execute_query(insert_query, (user1, user2))
                
                logger.info(f"✅ Amistad creada: {sender} <-> {receiver}")
            else:
                logger.info(f"✅ Solicitud rechazada: {request_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error respondiendo solicitud {request_id}: {e}")
            return False

    def get_pending_requests(self, user_id: str) -> List[Dict]:
        """Obtener solicitudes pendientes de un usuario"""
        query = '''
            SELECT 
                fr.id, fr.sender_id, fr.receiver_id, fr.status, fr.created_at,
                u.username AS sender_username, u.email AS sender_email
            FROM friend_requests fr
            JOIN users u ON u.id = fr.sender_id
            WHERE fr.receiver_id = %s AND fr.status = 'pending'
            ORDER BY fr.created_at DESC
        '''
        try:
            return self.execute_query(query, (user_id,), fetch_all=True) or []
        except Exception as e:
            logger.error(f"❌ Error obteniendo solicitudes pendientes: {e}")
            return []

    def get_sent_requests(self, user_id: str) -> List[Dict]:
        """Obtener solicitudes enviadas por un usuario"""
        query = '''
            SELECT 
                fr.id, fr.receiver_id, fr.status, fr.created_at,
                u.username AS receiver_username, u.email AS receiver_email
            FROM friend_requests fr
            JOIN users u ON u.id = fr.receiver_id
            WHERE fr.sender_id = %s
            ORDER BY fr.created_at DESC
        '''
        try:
            return self.execute_query(query, (user_id,), fetch_all=True) or []
        except Exception as e:
            logger.error(f"❌ Error obteniendo solicitudes enviadas: {e}")
            return []

    def get_friends(self, user_id: str) -> List[Dict]:
        """Obtener lista de amigos de un usuario"""
        query = '''
            SELECT 
                u.id, u.username, u.email, u.profile_pic,
                f.created_at as friendship_date, f.status
            FROM friendships f
            JOIN users u ON (
                (f.user_id_1 = %s AND u.id = f.user_id_2) OR
                (f.user_id_2 = %s AND u.id = f.user_id_1)
            )
            WHERE (f.user_id_1 = %s OR f.user_id_2 = %s)
              AND f.status = 'active'
            ORDER BY u.username
        '''
        try:
            return self.execute_query(query, (user_id, user_id, user_id, user_id), fetch_all=True) or []
        except Exception as e:
            logger.error(f"❌ Error obteniendo amigos: {e}")
            return []

    def search_users(self, query_str: str, exclude_ids: List[str], limit: int = 10) -> List[Dict]:
        """
        Buscar usuarios por username de forma segura contra SQL injection
        
        Args:
            query_str: Término de búsqueda
            exclude_ids: Lista de IDs a excluir (seguros)
            limit: Límite de resultados
            
        Returns:
            Lista de usuarios encontrados
        """
        try:
            # Validar inputs
            if not query_str or len(query_str.strip()) < 2:
                return []
            
            # Sanitizar query string
            query_str = query_str.strip()[:50]  # Limitar longitud
            
            # Construir placeholders seguros para exclude_ids
            if exclude_ids:
                # Validar que todos los IDs sean UUIDs válidos
                import uuid
                valid_exclude_ids = []
                for uid in exclude_ids:
                    try:
                        uuid.UUID(uid)  # Validar formato UUID
                        valid_exclude_ids.append(uid)
                    except ValueError:
                        continue
                
                if valid_exclude_ids:
                    # Construir query con número correcto de placeholders
                    placeholders = ','.join(['%s'] * len(valid_exclude_ids))
                    where_clause = f"AND id::text NOT IN ({placeholders})"
                    exclude_params = list(valid_exclude_ids)
                else:
                    where_clause = ""
                    exclude_params = []
            else:
                where_clause = ""
                exclude_params = []
            
            # Query segura con placeholders parametrizados
            query = f"""
                SELECT id, username, email FROM users
                WHERE (
                    username ILIKE %s OR email ILIKE %s
                ) 
                {where_clause}
                AND is_active = true
                ORDER BY username
                LIMIT %s
            """
            
            # Parámetros en orden seguro
            like_str = f"%{query_str}%"
            params = [like_str, like_str] + exclude_params + [limit]
            
            # Ejecutar query segura
            results = self.execute_query(query, tuple(params), fetch_all=True)
            
            if results:
                logger.info(f"✅ Búsqueda segura: {len(results)} resultados para '{query_str}'")
                return [dict(row) for row in results]
            else:
                return []
                
        except Exception as e:
            logger.error(f"❌ Error en búsqueda segura de usuarios: {e}")
            return []
    
    def are_friends(self, user_id_1: str, user_id_2: str) -> bool:
        """
        Verificar si dos usuarios son amigos
        
        Args:
            user_id_1: ID del primer usuario
            user_id_2: ID del segundo usuario
            
        Returns:
            True si son amigos, False si no
        """
        try:
            # Asegurar orden consistente
            user1, user2 = sorted([user_id_1, user_id_2])
            
            query = '''
                SELECT 1 FROM friendships 
                WHERE user_id_1 = %s AND user_id_2 = %s AND status = 'active'
                LIMIT 1
            '''
            result = self.execute_query(query, (user1, user2), fetch_one=True)
            return result is not None
        except Exception as e:
            logger.error(f"❌ Error verificando amistad: {e}")
            return False
    
    def get_friendship_status(self, user_id_1: str, user_id_2: str) -> Optional[str]:
        """
        Obtener estado de relación entre dos usuarios
        
        Args:
            user_id_1: ID del primer usuario
            user_id_2: ID del segundo usuario
            
        Returns:
            Estado de la relación (active, inactive, blocked) o None
        """
        try:
            user1, user2 = sorted([user_id_1, user_id_2])
            
            query = '''
                SELECT status FROM friendships 
                WHERE user_id_1 = %s AND user_id_2 = %s
                LIMIT 1
            '''
            result = self.execute_query(query, (user1, user2), fetch_one=True)
            return result['status'] if result else None
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado de amistad: {e}")
            return None
    
    def get_request_status(self, sender_id: str, receiver_id: str) -> Optional[str]:
        """
        Obtener estado de solicitud entre dos usuarios
        
        Args:
            sender_id: ID del emisor
            receiver_id: ID del receptor
            
        Returns:
            Estado de la solicitud o None
        """
        try:
            query = '''
                SELECT status FROM friend_requests 
                WHERE sender_id = %s AND receiver_id = %s
                LIMIT 1
            '''
            result = self.execute_query(query, (sender_id, receiver_id), fetch_one=True)
            return result['status'] if result else None
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado de solicitud: {e}")
            return None
