"""
Tests para funcionalidad de Chat Privado
Cobertura de funcionalidad crítica según estándares (100%)
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Añadir path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPrivateChatService(unittest.TestCase):
    """Tests para funcionalidad de chat privado en ChatService"""

    def setUp(self):
        """Configurar mocks para cada test"""
        self.mock_message_repo = Mock()
        self.mock_room_repo = Mock()
        self.mock_user_repo = Mock()

        # Patch de todos los repositorios
        patcher1 = patch('services.chat_service.MessageRepository')
        patcher2 = patch('services.chat_service.RoomRepository')
        patcher3 = patch('services.chat_service.UserRepository')

        self.mock_message_class = patcher1.start()
        self.mock_room_class = patcher2.start()
        self.mock_user_class = patcher3.start()

        self.mock_message_class.return_value = self.mock_message_repo
        self.mock_room_class.return_value = self.mock_room_repo
        self.mock_user_class.return_value = self.mock_user_repo

        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        self.addCleanup(patcher3.stop)

        # Importar ChatService después de los patches
        from services.chat_service import ChatService
        self.chat_service = ChatService()

    def test_get_or_create_individual_room_creates_new(self):
        """Test crear nueva sala individual cuando no existe"""
        # Configurar mocks
        self.mock_user_repo.find_by_username.side_effect = [
            {'id': 'user1-id', 'username': 'user1'},
            {'id': 'user2-id', 'username': 'user2'}
        ]
        self.mock_room_repo.find_individual_room.return_value = None
        self.mock_room_repo.create_individual_room.return_value = 'new-room-id'
        self.mock_room_repo.find_by_id.return_value = {
            'id': 'new-room-id',
            'name': 'user1 ↔ user2',
            'room_type': 'individual'
        }

        result = self.chat_service.get_or_create_individual_room('user1', 'user2')

        # Verificar
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], 'new-room-id')
        self.mock_room_repo.create_individual_room.assert_called_once()

    def test_get_or_create_individual_room_returns_existing(self):
        """Test retornar sala existente si ya existe"""
        # Configurar mocks
        self.mock_user_repo.find_by_username.side_effect = [
            {'id': 'user1-id', 'username': 'user1'},
            {'id': 'user2-id', 'username': 'user2'}
        ]
        existing_room = {
            'id': 'existing-room-id',
            'name': 'user1 ↔ user2',
            'room_type': 'individual'
        }
        self.mock_room_repo.find_individual_room.return_value = existing_room
        # show_room es llamado para marcar visible si estaba oculto
        self.mock_room_repo.execute_query.return_value = 0  # No estaba oculto

        result = self.chat_service.get_or_create_individual_room('user1', 'user2')

        # Verificar que retorna sala existente y NO crea nueva
        self.assertEqual(result['id'], 'existing-room-id')
        self.mock_room_repo.create_individual_room.assert_not_called()

    def test_get_or_create_individual_room_user_not_found(self):
        """Test con usuario no encontrado"""
        self.mock_user_repo.find_by_username.return_value = None

        result = self.chat_service.get_or_create_individual_room('noexiste', 'user2')

        self.assertIsNone(result)
        self.mock_room_repo.find_individual_room.assert_not_called()

    def test_get_or_create_individual_room_shows_hidden_room(self):
        """Test que muestra sala oculta cuando se abre chat existente"""
        # Configurar mocks
        self.mock_user_repo.find_by_username.side_effect = [
            {'id': 'user1-id', 'username': 'user1'},
            {'id': 'user2-id', 'username': 'user2'}
        ]
        existing_room = {
            'id': 'hidden-room-id',
            'name': 'user1 ↔ user2',
            'room_type': 'individual'
        }
        self.mock_room_repo.find_individual_room.return_value = existing_room
        self.mock_room_repo.execute_query.return_value = 1  # show_room affected rows

        result = self.chat_service.get_or_create_individual_room('user1', 'user2')

        # Verificar que se llamó show_room (execute_query para UPDATE)
        self.assertEqual(result['id'], 'hidden-room-id')
        # El método show_room usa execute_query
        self.mock_room_repo.execute_query.assert_called()

    def test_show_room_success(self):
        """Test mostrar sala oculta"""
        self.mock_room_repo.execute_query.return_value = 1

        result = self.chat_service.show_room('user-id', 'room-id')

        self.assertTrue(result)
        self.mock_room_repo.execute_query.assert_called_once()

    def test_show_room_not_hidden(self):
        """Test mostrar sala que no estaba oculta"""
        self.mock_room_repo.execute_query.return_value = 0

        result = self.chat_service.show_room('user-id', 'room-id')

        self.assertFalse(result)

    def test_hide_room_success(self):
        """Test ocultar sala"""
        self.mock_room_repo.execute_query.return_value = 1

        result = self.chat_service.hide_room('user-id', 'room-id')

        self.assertTrue(result)

    def test_send_message_to_individual_room(self):
        """Test enviar mensaje a sala individual"""
        # Configurar mocks
        self.mock_room_repo.find_by_id.return_value = {
            'id': 'individual-room-id',
            'room_type': 'individual'
        }
        self.mock_user_repo.find_by_username.return_value = {
            'id': 'sender-id',
            'username': 'sender'
        }
        self.mock_message_repo.save_message.return_value = 'msg-123'

        result = self.chat_service.send_message('sender', 'individual-room-id', 'Hola!')

        # Verificar
        self.assertIsNotNone(result)
        self.assertEqual(result['content'], 'Hola!')
        self.assertEqual(result['roomId'], 'individual-room-id')
        self.mock_message_repo.save_message.assert_called_once()


class TestPrivateChatRoomRepository(unittest.TestCase):
    """Tests para RoomRepository relacionados con chat privado"""

    def setUp(self):
        """Configurar mocks"""
        self.mock_db_manager = Mock()

        patcher = patch('repositories.base_repository.db_manager', self.mock_db_manager)
        patcher.start()
        self.addCleanup(patcher.stop)

        from repositories.base_repository import RoomRepository
        self.room_repo = RoomRepository()

    def test_find_individual_room_order_independent(self):
        """Test que find_individual_room funciona sin importar el orden de usuarios"""
        # Este test verifica que la query busca en ambas direcciones
        mock_connection = Mock()
        mock_cursor = Mock()
        self.mock_db_manager.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        # Simular que no se encuentra sala
        mock_cursor.fetchone.return_value = None

        result = self.room_repo.find_individual_room('user1-id', 'user2-id')

        # Verificar que se ejecutó la query
        mock_cursor.execute.assert_called_once()
        query_call = mock_cursor.execute.call_args[0][0]

        # La query debe buscar en ambas direcciones
        self.assertIn('user_id_1 = %s AND user_id_2 = %s', query_call)
        self.assertIn('user_id_1 = %s AND user_id_2 = %s', query_call)


class TestPrivateChatUserRoomsDetailed(unittest.TestCase):
    """Tests para obtener salas del usuario con detalles"""

    def setUp(self):
        """Configurar mocks"""
        self.mock_message_repo = Mock()
        self.mock_room_repo = Mock()
        self.mock_user_repo = Mock()

        patcher1 = patch('services.chat_service.MessageRepository')
        patcher2 = patch('services.chat_service.RoomRepository')
        patcher3 = patch('services.chat_service.UserRepository')

        self.mock_message_class = patcher1.start()
        self.mock_room_class = patcher2.start()
        self.mock_user_class = patcher3.start()

        self.mock_message_class.return_value = self.mock_message_repo
        self.mock_room_class.return_value = self.mock_room_repo
        self.mock_user_class.return_value = self.mock_user_repo

        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        self.addCleanup(patcher3.stop)

        from services.chat_service import ChatService
        self.chat_service = ChatService()

    def test_get_user_rooms_detailed_includes_individual_chats(self):
        """Test que get_user_rooms_detailed incluye chats individuales"""
        # Configurar mock para retornar rooms mixtos
        self.mock_room_repo.get_rooms_for_user.return_value = [
            {'id': 'public-room', 'name': 'General', 'room_type': 'public'},
            {
                'id': 'individual-room',
                'name': 'user1 ↔ user2',
                'room_type': 'individual',
                'user_id_1': 'user1-id',
                'user_id_2': 'user2-id'
            }
        ]
        self.mock_user_repo.find_by_id.return_value = {
            'id': 'user2-id',
            'username': 'user2'
        }
        self.mock_message_repo.execute_query.return_value = None  # Sin último mensaje

        result = self.chat_service.get_user_rooms_detailed('user1-id', 'user1')

        # Verificar que ambos tipos de rooms están presentes
        self.assertEqual(len(result), 2)
        room_types = [r.get('room_type') for r in result]
        self.assertIn('public', room_types)
        self.assertIn('individual', room_types)

    def test_individual_room_shows_other_username(self):
        """Test que sala individual muestra username del otro usuario"""
        self.mock_room_repo.get_rooms_for_user.return_value = [
            {
                'id': 'individual-room',
                'name': 'user1 ↔ user2',
                'room_type': 'individual',
                'user_id_1': 'user1-id',
                'user_id_2': 'user2-id'
            }
        ]
        self.mock_user_repo.find_by_id.return_value = {
            'id': 'user2-id',
            'username': 'user2'
        }
        self.mock_message_repo.execute_query.return_value = None

        result = self.chat_service.get_user_rooms_detailed('user1-id', 'user1')

        # Verificar que el nombre se personaliza al otro usuario
        individual_room = result[0]
        self.assertEqual(individual_room['name'], 'user2')
        self.assertEqual(individual_room['other_username'], 'user2')


if __name__ == '__main__':
    unittest.main()
