"""
Validation Schemas
Define esquemas de validación para datos de entrada
"""
from typing import Dict, List, Optional, Any
import re

class ValidationError(Exception):
    """Excepción personalizada para errores de validación"""
    pass

class BaseValidator:
    """Clase base para validadores"""
    
    @staticmethod
    def validate_string(value: Any, field_name: str, min_length: int = 1, max_length: int = 255, required: bool = True) -> str:
        """Validar campo string"""
        if value is None or value == "":
            if required:
                raise ValidationError(f"{field_name} es requerido")
            return ""
        
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} debe ser una cadena de texto")
        
        value = value.strip()
        
        if len(value) < min_length:
            raise ValidationError(f"{field_name} debe tener al menos {min_length} caracteres")
        
        if len(value) > max_length:
            raise ValidationError(f"{field_name} no puede tener más de {max_length} caracteres")
        
        return value
    
    @staticmethod
    def validate_username(username: Any) -> str:
        """Validar username con reglas específicas"""
        username = BaseValidator.validate_string(username, "Username", min_length=3, max_length=50)
        
        # Solo letras, números y guiones bajos
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("Username solo puede contener letras, números y guiones bajos")
        
        return username
    
    @staticmethod
    def validate_room_id(room_id: Any) -> str:
        """Validar ID de sala"""
        room_id = BaseValidator.validate_string(room_id, "Room ID", min_length=1, max_length=10)
        
        # Solo letras y números
        if not re.match(r'^[a-zA-Z0-9]+$', room_id):
            raise ValidationError("Room ID solo puede contener letras y números")
        
        return room_id
    
    @staticmethod
    def validate_message_content(content: Any) -> str:
        """Validar contenido de mensaje"""
        content = BaseValidator.validate_string(content, "Message content", min_length=1, max_length=1000)
        
        # Remover caracteres de control peligrosos
        sanitized = ''.join(char for char in content if ord(char) >= 32 or char in '\n\r\t')
        
        if not sanitized.strip():
            raise ValidationError("El mensaje no puede estar vacío después de la sanitización")
        
        return sanitized.strip()

class LoginValidator(BaseValidator):
    """Validador para datos de login"""
    
    @classmethod
    def validate(cls, data: Dict) -> Dict[str, str]:
        """
        Validar datos de login
        
        Args:
            data: Diccionario con username y password
            
        Returns:
            Diccionario con datos validados
            
        Raises:
            ValidationError: Si hay errores de validación
        """
        if not isinstance(data, dict):
            raise ValidationError("Los datos deben ser un objeto JSON")
        
        # Validar username
        username = cls.validate_username(data.get('username'))
        
        # Validar password
        password = cls.validate_string(data.get('password'), "Password", min_length=1, max_length=255)
        
        return {
            'username': username,
            'password': password
        }

class MessageValidator(BaseValidator):
    """Validador para datos de mensaje"""
    
    @classmethod
    def validate(cls, data: Dict) -> Dict[str, str]:
        """
        Validar datos de mensaje
        
        Args:
            data: Diccionario con username, room y message
            
        Returns:
            Diccionario con datos validados
            
        Raises:
            ValidationError: Si hay errores de validación
        """
        if not isinstance(data, dict):
            raise ValidationError("Los datos deben ser un objeto JSON")
        
        # Validar campos requeridos
        username = cls.validate_username(data.get('username'))
        room_id = cls.validate_room_id(data.get('room'))
        content = cls.validate_message_content(data.get('message'))
        
        return {
            'username': username,
            'room': room_id,
            'message': content
        }

class JoinRoomValidator(BaseValidator):
    """Validador para unirse a sala"""
    
    @classmethod
    def validate(cls, data: Dict) -> Dict[str, str]:
        """
        Validar datos para unirse a sala
        
        Args:
            data: Diccionario con username y room
            
        Returns:
            Diccionario con datos validados
            
        Raises:
            ValidationError: Si hay errores de validación
        """
        if not isinstance(data, dict):
            raise ValidationError("Los datos deben ser un objeto JSON")
        
        username = cls.validate_username(data.get('username'))
        room_id = cls.validate_room_id(data.get('room'))
        
        return {
            'username': username,
            'room': room_id
        }