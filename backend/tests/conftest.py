"""
Test Configuration
Configuración base para tests de la aplicación
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch

# Añadir el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_db_connection():
    """Mock de conexión a base de datos para tests"""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor

@pytest.fixture
def sample_user_data():
    """Datos de usuario de ejemplo para tests"""
    return {
        'id': 'test-user-id-123',
        'username': 'testuser',
        'email': 'test@example.com',
        'password_hash': 'testpassword',
        'is_active': True
    }

@pytest.fixture
def sample_message_data():
    """Datos de mensaje de ejemplo para tests"""
    return {
        'id': 'test-message-id-123',
        'user_id': 'test-user-id-123',
        'room_id': 'R1',
        'content': 'Mensaje de prueba',
        'created_at': '2025-10-10T10:00:00',
        'is_deleted': False
    }

@pytest.fixture
def sample_room_data():
    """Datos de sala de ejemplo para tests"""
    return {
        'id': 'R1',
        'name': 'Sala de Prueba',
        'description': 'Sala para testing',
        'is_active': True
    }