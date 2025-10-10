"""
Unit Tests for Services
Tests de lógica de negocio
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Añadir path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestAuthService(unittest.TestCase):
    """Tests para AuthService"""
    
    def setUp(self):
        """Configurar mocks para cada test"""
        # Mock del user repository
        self.mock_user_repo = Mock()
        
        # Patch del UserRepository para usar nuestro mock
        patcher = patch('services.auth_service.UserRepository')
        self.mock_repo_class = patcher.start()
        self.mock_repo_class.return_value = self.mock_user_repo
        self.addCleanup(patcher.stop)
        
        # Importar AuthService después del patch
        from services.auth_service import AuthService
        self.auth_service = AuthService()
    
    def test_authenticate_user_success(self):
        """Test de autenticación exitosa"""
        # Configurar mock para retornar usuario válido
        self.mock_user_repo.find_by_username.return_value = {
            'id': 'test-id-123',
            'username': 'testuser',
            'email': 'test@example.com',
            'password_hash': 'testpassword',
            'last_login': None
        }
        
        result = self.auth_service.authenticate_user('testuser', 'testpassword')
        
        # Verificar que se llamó al método correcto
        self.mock_user_repo.find_by_username.assert_called_once_with('testuser')
        self.mock_user_repo.update_last_login.assert_called_once_with('test-id-123')
        
        # Verificar resultado
        self.assertIsNotNone(result)
        self.assertEqual(result['username'], 'testuser')
        self.assertEqual(result['id'], 'test-id-123')
    
    def test_authenticate_user_not_found(self):
        """Test con usuario no encontrado"""
        self.mock_user_repo.find_by_username.return_value = None
        
        result = self.auth_service.authenticate_user('noexiste', 'password')
        
        self.assertIsNone(result)
        self.mock_user_repo.find_by_username.assert_called_once_with('noexiste')
        self.mock_user_repo.update_last_login.assert_not_called()
    
    def test_authenticate_user_wrong_password(self):
        """Test con password incorrecto"""
        self.mock_user_repo.find_by_username.return_value = {
            'id': 'test-id-123',
            'username': 'testuser',
            'password_hash': 'correctpassword'
        }
        
        result = self.auth_service.authenticate_user('testuser', 'wrongpassword')
        
        self.assertIsNone(result)
        self.mock_user_repo.update_last_login.assert_not_called()

class TestChatService(unittest.TestCase):
    """Tests para ChatService"""
    
    def setUp(self):
        """Configurar mocks para cada test"""
        self.mock_message_repo = Mock()
        self.mock_room_repo = Mock()
        self.mock_user_repo = Mock()
        
        # Patch de todos los repositorios
        patcher1 = patch('services.chat_service.MessageRepository')
        patcher2 = patch('services.chat_service.RoomRepository')
        patcher3 = patch('services.chat_service.UserRepository')
        
        self.mock_message_repo_class = patcher1.start()
        self.mock_room_repo_class = patcher2.start()
        self.mock_user_repo_class = patcher3.start()
        
        self.mock_message_repo_class.return_value = self.mock_message_repo
        self.mock_room_repo_class.return_value = self.mock_room_repo
        self.mock_user_repo_class.return_value = self.mock_user_repo
        
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        self.addCleanup(patcher3.stop)
        
        # Importar ChatService después de los patches
        from services.chat_service import ChatService
        self.chat_service = ChatService()
    
    def test_send_message_success(self):
        """Test de envío de mensaje exitoso"""
        # Configurar mocks
        self.mock_room_repo.find_by_id.return_value = {
            'id': 'R1', 'name': 'Test Room', 'is_active': True
        }
        self.mock_user_repo.find_by_username.return_value = {
            'id': 'user-123', 'username': 'testuser'
        }
        self.mock_message_repo.save_message.return_value = 'message-123'
        
        result = self.chat_service.send_message('testuser', 'R1', 'Hola mundo')
        
        # Verificar llamadas
        self.mock_room_repo.find_by_id.assert_called_once_with('R1')
        self.mock_user_repo.find_by_username.assert_called_once_with('testuser')
        self.mock_message_repo.save_message.assert_called_once()
        
        # Verificar resultado
        self.assertIsNotNone(result)
        self.assertEqual(result['username'], 'testuser')
        self.assertEqual(result['roomId'], 'R1')
        self.assertEqual(result['content'], 'Hola mundo')
    
    def test_send_message_room_not_found(self):
        """Test con sala no encontrada"""
        self.mock_room_repo.find_by_id.return_value = None
        
        result = self.chat_service.send_message('testuser', 'NOEXISTE', 'Hola')
        
        self.assertIsNone(result)
        self.mock_message_repo.save_message.assert_not_called()
    
    def test_send_message_empty_content(self):
        """Test con contenido vacío"""
        result = self.chat_service.send_message('testuser', 'R1', '   ')
        
        self.assertIsNone(result)
        self.mock_room_repo.find_by_id.assert_not_called()
    
    def test_get_room_messages(self):
        """Test de obtención de mensajes"""
        # Configurar mock para retornar mensajes
        self.mock_message_repo.get_messages_by_room.return_value = [
            {
                'id': 'msg-1',
                'room_id': 'R1',
                'username': 'user1',
                'content': 'Mensaje 1',
                'created_at': Mock(isoformat=Mock(return_value='2025-10-10T10:00:00'))
            },
            {
                'id': 'msg-2',
                'room_id': 'R1',
                'username': 'user2',
                'content': 'Mensaje 2',
                'created_at': Mock(isoformat=Mock(return_value='2025-10-10T10:01:00'))
            }
        ]
        
        result = self.chat_service.get_room_messages('R1')
        
        # Verificar llamada
        self.mock_message_repo.get_messages_by_room.assert_called_once_with(
            room_id='R1', limit=50, offset=0
        )
        
        # Verificar resultado
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['username'], 'user1')
        self.assertEqual(result[1]['username'], 'user2')

if __name__ == '__main__':
    unittest.main()