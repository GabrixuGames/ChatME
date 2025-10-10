"""
Unit Tests for Validators
Tests de validación de datos de entrada
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Añadir path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validators import ValidationError, LoginValidator, MessageValidator, JoinRoomValidator

class TestLoginValidator(unittest.TestCase):
    """Tests para LoginValidator"""
    
    def test_valid_login_data(self):
        """Test con datos válidos"""
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        result = LoginValidator.validate(data)
        self.assertEqual(result['username'], 'testuser')
        self.assertEqual(result['password'], 'testpassword')
    
    def test_missing_username(self):
        """Test con username faltante"""
        data = {'password': 'testpassword'}
        with self.assertRaises(ValidationError) as context:
            LoginValidator.validate(data)
        self.assertIn('Username', str(context.exception))
    
    def test_missing_password(self):
        """Test con password faltante"""
        data = {'username': 'testuser'}
        with self.assertRaises(ValidationError) as context:
            LoginValidator.validate(data)
        self.assertIn('Password', str(context.exception))
    
    def test_invalid_username_characters(self):
        """Test con caracteres inválidos en username"""
        data = {
            'username': 'test@user!',
            'password': 'testpassword'
        }
        with self.assertRaises(ValidationError) as context:
            LoginValidator.validate(data)
        self.assertIn('solo puede contener', str(context.exception))
    
    def test_username_too_short(self):
        """Test con username muy corto"""
        data = {
            'username': 'ab',
            'password': 'testpassword'
        }
        with self.assertRaises(ValidationError) as context:
            LoginValidator.validate(data)
        self.assertIn('al menos 3', str(context.exception))

class TestMessageValidator(unittest.TestCase):
    """Tests para MessageValidator"""
    
    def test_valid_message_data(self):
        """Test con datos de mensaje válidos"""
        data = {
            'username': 'testuser',
            'room': 'R1',
            'message': 'Hola mundo'
        }
        result = MessageValidator.validate(data)
        self.assertEqual(result['username'], 'testuser')
        self.assertEqual(result['room'], 'R1')
        self.assertEqual(result['message'], 'Hola mundo')
    
    def test_message_content_sanitization(self):
        """Test de sanitización de contenido"""
        data = {
            'username': 'testuser',
            'room': 'R1',
            'message': '  Mensaje con espacios  \n\r'
        }
        result = MessageValidator.validate(data)
        self.assertEqual(result['message'], 'Mensaje con espacios')
    
    def test_empty_message(self):
        """Test con mensaje vacío"""
        data = {
            'username': 'testuser',
            'room': 'R1',
            'message': '   '
        }
        with self.assertRaises(ValidationError) as context:
            MessageValidator.validate(data)
        self.assertIn('vacío', str(context.exception))
    
    def test_message_too_long(self):
        """Test con mensaje muy largo"""
        data = {
            'username': 'testuser',
            'room': 'R1',
            'message': 'x' * 1001  # Más de 1000 caracteres
        }
        with self.assertRaises(ValidationError) as context:
            MessageValidator.validate(data)
        self.assertIn('1000', str(context.exception))

class TestJoinRoomValidator(unittest.TestCase):
    """Tests para JoinRoomValidator"""
    
    def test_valid_join_data(self):
        """Test con datos válidos para unirse a sala"""
        data = {
            'username': 'testuser',
            'room': 'R1'
        }
        result = JoinRoomValidator.validate(data)
        self.assertEqual(result['username'], 'testuser')
        self.assertEqual(result['room'], 'R1')
    
    def test_invalid_room_id(self):
        """Test con ID de sala inválido"""
        data = {
            'username': 'testuser',
            'room': 'Room-1!'
        }
        with self.assertRaises(ValidationError) as context:
            JoinRoomValidator.validate(data)
        self.assertIn('solo puede contener', str(context.exception))

if __name__ == '__main__':
    unittest.main()