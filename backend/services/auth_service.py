"""
Authentication Service
Maneja toda la lógica de negocio relacionada con autenticación
"""
from typing import Optional, Dict
from repositories.base_repository import UserRepository
import logging
import bcrypt

logger = logging.getLogger(__name__)

class AuthService:
    """
    Servicio de autenticación
    Encapsula la lógica de negocio para login, logout, etc.
    """

    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Hashear password usando bcrypt
        
        Args:
            password: Password en texto plano
            
        Returns:
            Password hasheado como string
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def _verify_password(password: str, hashed_password: str) -> bool:
        """
        Verificar password contra hash
        
        Args:
            password: Password en texto plano
            hashed_password: Hash almacenado en base de datos
            
        Returns:
            True si el password es correcto, False si no
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def register_user(self, username: str, email: str, password: str) -> Optional[str]:
        """
        Registrar usuario nuevo con password hasheado de forma segura
        
        Args:
            username: Username del usuario
            email: Email del usuario
            password: Password en texto plano
            
        Returns:
            ID del usuario creado o None
        """
        try:
            # Hashear password de forma segura con bcrypt
            password_hash = self._hash_password(password)
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
        Autenticar usuario con username y password verificando hash
        
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
            
            # Verificar password usando bcrypt
            if not self._verify_password(password, user['password_hash']):
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