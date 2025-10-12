"""
Authentication Service
Maneja toda la lógica de negocio relacionada con autenticación
"""
from typing import Optional, Dict
from repositories.base_repository import UserRepository
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """
    Servicio de autenticación
    Encapsula la lógica de negocio para login, logout, etc.
    """

    def register_user(self, username: str, email: str, password: str) -> Optional[str]:
        """
        Registrar usuario nuevo
        Args:
            username: Username del usuario
            email: Email del usuario
            password: Password en texto plano
        Returns:
            ID del usuario creado o None
        """
        try:
            # TODO: Usar bcrypt en producción
            password_hash = password
            user_id = self.user_repository.create_user(username, email, password_hash)
            if user_id:
                logger.info(f"✅ Usuario registrado: {username}")
                return user_id
            else:
                logger.error(f"❌ Error al registrar usuario: {username}")
                return None
        except Exception as e:
            logger.error(f"❌ Error en registro: {e}")
            return None
    
    def __init__(self):
        self.user_repository = UserRepository()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Autenticar usuario con username y password
        
        Args:
            username: Username del usuario
            password: Password en texto plano
            
        Returns:
            Dict con información del usuario si es válido, None si no
        """
        try:
            # Buscar usuario en base de datos
            user = self.user_repository.find_by_username(username)
            
            if not user:
                logger.warning(f"🔍 Usuario no encontrado: {username}")
                return None
            
            # Verificar password (por ahora comparación directa)
            # TODO: Implementar bcrypt para producción
            if user['password_hash'] != password:
                logger.warning(f"🔐 Password incorrecto para usuario: {username}")
                return None
            
            # Actualizar último login
            self.user_repository.update_last_login(user['id'])
            
            logger.info(f"✅ Usuario autenticado exitosamente: {username}")
            
            return {
                'id': str(user['id']),
                'username': user['username'],
                'email': user['email'],
                'last_login': user['last_login']
            }
            
        except Exception as e:
            logger.error(f"❌ Error en autenticación: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Obtener información de usuario por username"""
        try:
            user = self.user_repository.find_by_username(username)
            if user:
                return {
                    'id': str(user['id']),
                    'username': user['username'],
                    'email': user['email']
                }
            return None
        except Exception as e:
            logger.error(f"❌ Error obteniendo usuario: {e}")
            return None