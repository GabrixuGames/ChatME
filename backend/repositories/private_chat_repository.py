"""
Private Chat Repository
Maneja operaciones para chats y mensajes individuales
"""
from .base_repository import BaseRepository
from typing import Optional, List, Dict

class PrivateChatRepository(BaseRepository):
    def create_private_chat(self, user1_username: str, user2_username: str, is_temporary: bool = True) -> Optional[str]:
        # Validar existencia de ambos usuarios
        user_query = "SELECT id FROM users WHERE username = %s AND is_active = true"
        user1 = self.execute_query(user_query, (user1_username,), fetch_one=True)
        user2 = self.execute_query(user_query, (user2_username,), fetch_one=True)
        if not user1 or not user2:
            raise ValueError(f"Usuario no encontrado: {'user1' if not user1 else 'user2'}")
        query = """
            INSERT INTO private_chats (user1_id, user2_id, is_temporary)
            VALUES (%s, %s, %s)
            RETURNING id
        """
        result = self.execute_query(query, (user1['id'], user2['id'], is_temporary), fetch_one=True)
        return result['id'] if result else None

    def get_private_chat(self, chat_id: str) -> Optional[Dict]:
        query = "SELECT * FROM private_chats WHERE id = %s"
        return self.execute_query(query, (chat_id,), fetch_one=True)

    def find_chat_between_users(self, user1_username: str, user2_username: str) -> Optional[Dict]:
        query = """
            SELECT * FROM private_chats
            WHERE (user1_id = (SELECT id FROM users WHERE username = %s) AND user2_id = (SELECT id FROM users WHERE username = %s))
               OR (user1_id = (SELECT id FROM users WHERE username = %s) AND user2_id = (SELECT id FROM users WHERE username = %s))
        """
        return self.execute_query(query, (user1_username, user2_username, user2_username, user1_username), fetch_one=True)

class PrivateMessageRepository(BaseRepository):
    def save_private_message(self, chat_id: str, sender_id: str, content: str) -> Optional[str]:
        query = """
            INSERT INTO private_messages (private_chat_id, sender_id, content)
            VALUES (%s, %s, %s)
            RETURNING id
        """
        result = self.execute_query(query, (chat_id, sender_id, content), fetch_one=True)
        return result['id'] if result else None

    def get_messages_by_chat(self, chat_id: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        query = """
            SELECT pm.id, pm.content, pm.created_at, u.username, pm.sender_id
            FROM private_messages pm
            JOIN users u ON pm.sender_id = u.id
            WHERE pm.private_chat_id = %s
            ORDER BY pm.created_at DESC
            LIMIT %s OFFSET %s
        """
        messages = self.execute_query(query, (chat_id, limit, offset), fetch_all=True)
        return list(reversed(messages)) if messages else []
