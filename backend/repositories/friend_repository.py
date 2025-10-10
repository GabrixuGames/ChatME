from typing import List, Optional, Dict
from utils.database import db_manager
import psycopg2.extras

class FriendRepository:
    def remove_friend(self, user_id: str, friend_id: str) -> bool:
        query = '''
            DELETE FROM friends_list WHERE (user_id = %s AND friend_id = %s) OR (user_id = %s AND friend_id = %s)
        '''
        connection = self.db_manager.get_connection()
        cursor = connection.cursor()
        cursor.execute(query, (user_id, friend_id, friend_id, user_id))
        connection.commit()
        affected = cursor.rowcount
        self.db_manager.return_connection(connection)
        return affected > 0
    def __init__(self):
        self.db_manager = db_manager

    def send_request(self, sender_id: str, receiver_id: str) -> Optional[str]:
        query = '''
            INSERT INTO friend_requests (sender_id, receiver_id)
            VALUES (%s, %s)
            RETURNING id
        '''
        connection = self.db_manager.get_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(query, (sender_id, receiver_id))
        connection.commit()
        result = cursor.fetchone()
        self.db_manager.return_connection(connection)
        return result['id'] if result else None

    def respond_request(self, request_id: str, status: str) -> bool:
        # Obtener la solicitud para saber los IDs
        get_query = "SELECT sender_id, receiver_id FROM friend_requests WHERE id = %s"
        connection = self.db_manager.get_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(get_query, (request_id,))
        req = cursor.fetchone()
        if not req:
            self.db_manager.return_connection(connection)
            return False
        # Actualizar estado de la solicitud
        update_query = '''
            UPDATE friend_requests SET status = %s, responded_at = NOW()
            WHERE id = %s
        '''
        cursor.execute(update_query, (status, request_id))
        # Si se acepta, crear relación simétrica en friends_list
        if status == 'accepted':
            insert_query = '''
                INSERT INTO friends_list (user_id, friend_id) VALUES (%s, %s), (%s, %s)
            '''
            cursor.execute(insert_query, (req['sender_id'], req['receiver_id'], req['receiver_id'], req['sender_id']))
        connection.commit()
        affected = cursor.rowcount
        self.db_manager.return_connection(connection)
        return affected > 0

    def get_pending_requests(self, user_id: str) -> List[Dict]:
        query = '''
            SELECT fr.*, u.username AS sender_username FROM friend_requests fr
            JOIN users u ON u.id = fr.sender_id
            WHERE fr.receiver_id = %s AND fr.status = 'pending'
        '''
        connection = self.db_manager.get_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        self.db_manager.return_connection(connection)
        return results

    def get_sent_requests(self, user_id: str) -> List[Dict]:
        query = '''
            SELECT * FROM friend_requests WHERE sender_id = %s
        '''
        connection = self.db_manager.get_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        self.db_manager.return_connection(connection)
        return results

    def get_friends(self, user_id: str) -> List[Dict]:
        query = '''
            SELECT u.id, u.username, u.email, u.profile_pic FROM friends_list f
            JOIN users u ON u.id = f.friend_id
            WHERE f.user_id = %s
        '''
        connection = self.db_manager.get_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        self.db_manager.return_connection(connection)
        return results

    def search_users(self, query_str: str, exclude_ids: List[str], limit: int = 10) -> List[Dict]:
        # Si exclude_ids está vacío, poner un valor imposible
        if not exclude_ids:
            exclude_ids = ['0']
        query = f"""
            SELECT id, username FROM users
            WHERE (
                username ILIKE %s OR id::text ILIKE %s
            ) AND id NOT IN ({','.join(['%s']*len(exclude_ids))})
            LIMIT %s
        """
        like_str = f"%{query_str}%"
        connection = self.db_manager.get_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        params = [like_str, like_str] + list(exclude_ids) + [limit]
        cursor.execute(query, params)
        results = cursor.fetchall()
        self.db_manager.return_connection(connection)
        return results
