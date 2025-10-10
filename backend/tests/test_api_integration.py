"""
Integration Tests for API
Tests de integración para endpoints HTTP
"""
import unittest
import json
import sys
import os
from unittest.mock import patch, Mock

# Añadir path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestAPIIntegration(unittest.TestCase):
    """Tests de integración para la API"""
    
    def setUp(self):
        """Configurar la aplicación de test"""
        # Mock de los servicios para evitar conexiones reales a DB
        self.mock_auth_service = Mock()
        self.mock_chat_service = Mock()
        
        # Patches para los servicios
        patcher1 = patch('app.auth_service', self.mock_auth_service)
        patcher2 = patch('app.chat_service', self.mock_chat_service)
        
        patcher1.start()
        patcher2.start()
        
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        
        # Importar y configurar la app después de los patches
        from app import app
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def tearDown(self):
        """Limpiar después de cada test"""
        self.app_context.pop()
    
    def test_home_endpoint(self):
        """Test del endpoint principal"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_login_success(self):
        """Test de login exitoso"""
        # Configurar mock para login exitoso
        self.mock_auth_service.authenticate_user.return_value = {
            'id': 'user-123',
            'username': 'testuser',
            'email': 'test@example.com'
        }
        
        response = self.client.post('/procesar_login',
            data=json.dumps({
                'username': 'testuser',
                'password': 'testpassword'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('Login exitoso', data['message'])
        self.assertEqual(data['username'], 'testuser')
    
    def test_login_invalid_credentials(self):
        """Test de login con credenciales inválidas"""
        # Configurar mock para login fallido
        self.mock_auth_service.authenticate_user.return_value = None
        
        response = self.client.post('/procesar_login',
            data=json.dumps({
                'username': 'testuser',
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('incorrectas', data['error'])
    
    def test_login_missing_data(self):
        """Test de login con datos faltantes"""
        response = self.client.post('/procesar_login',
            data=json.dumps({
                'username': 'testuser'
                # password faltante
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('requeridos', data['error'])
    
    def test_login_invalid_json(self):
        """Test de login con JSON inválido"""
        response = self.client.post('/procesar_login',
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_logout(self):
        """Test de logout"""
        # Simular sesión activa
        with self.client.session_transaction() as sess:
            sess['username'] = 'testuser'
        
        response = self.client.post('/logout')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('cerrada', data['message'])
    
    def test_verificar_sesion_authenticated(self):
        """Test de verificación de sesión con usuario autenticado"""
        # Simular sesión activa
        with self.client.session_transaction() as sess:
            sess['username'] = 'testuser'
        
        response = self.client.get('/verificar_sesion')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['authenticated'])
        self.assertEqual(data['username'], 'testuser')
    
    def test_verificar_sesion_not_authenticated(self):
        """Test de verificación de sesión sin autenticar"""
        response = self.client.get('/verificar_sesion')
        self.assertEqual(response.status_code, 401)
        
        data = json.loads(response.data)
        self.assertFalse(data['authenticated'])

if __name__ == '__main__':
    unittest.main()