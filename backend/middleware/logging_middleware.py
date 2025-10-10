"""
Logging Middleware
Proporciona logging estructurado y profesional para la aplicación
"""
import logging
import sys
from datetime import datetime
from flask import request, g
import time

def setup_logging():
    """
    Configurar el sistema de logging de la aplicación
    """
    # Crear formateador personalizado
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Handler para archivo (opcional)
    # file_handler = logging.FileHandler('chatapp.log')
    # file_handler.setFormatter(formatter)
    # file_handler.setLevel(logging.DEBUG)
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    # root_logger.addHandler(file_handler)
    
    # Configurar loggers específicos
    logging.getLogger('werkzeug').setLevel(logging.WARNING)  # Reducir ruido de Flask
    logging.getLogger('socketio').setLevel(logging.WARNING)  # Reducir ruido de SocketIO
    
    return logging.getLogger('chatapp')

def log_request_middleware(app):
    """
    Middleware para logging de requests HTTP
    """
    @app.before_request
    def before_request():
        g.start_time = time.time()
        
        # Log de request entrante
        logger = logging.getLogger('chatapp.requests')
        logger.info(f"🔄 {request.method} {request.path} | IP: {request.remote_addr}")
        
        # Log de datos POST/PUT (sin passwords)
        if request.method in ['POST', 'PUT'] and request.is_json:
            data = request.get_json()
            if data:
                # Filtrar información sensible
                safe_data = {k: v for k, v in data.items() if k not in ['password', 'token']}
                if safe_data:
                    logger.debug(f"📝 Request data: {safe_data}")
    
    @app.after_request
    def after_request(response):
        # Calcular tiempo de respuesta
        if hasattr(g, 'start_time'):
            duration = round((time.time() - g.start_time) * 1000, 2)
        else:
            duration = 0
        
        # Log de respuesta
        logger = logging.getLogger('chatapp.requests')
        status_emoji = "✅" if response.status_code < 400 else "❌"
        logger.info(f"{status_emoji} {request.method} {request.path} | {response.status_code} | {duration}ms")
        
        return response

class SocketIOLogger:
    """
    Logger especializado para eventos de Socket.IO
    """
    def __init__(self):
        self.logger = logging.getLogger('chatapp.socketio')
    
    def log_connection(self, sid, username=None):
        """Log de nueva conexión Socket.IO"""
        user_info = f"({username})" if username else ""
        self.logger.info(f"🔌 Nueva conexión Socket.IO | SID: {sid} {user_info}")
    
    def log_disconnection(self, sid, username=None):
        """Log de desconexión Socket.IO"""
        user_info = f"({username})" if username else ""
        self.logger.info(f"🔌 Desconexión Socket.IO | SID: {sid} {user_info}")
    
    def log_join_room(self, sid, room_id, username=None):
        """Log de unión a sala"""
        user_info = f"({username})" if username else ""
        self.logger.info(f"🏠 Usuario se unió a sala | SID: {sid} {user_info} | Sala: {room_id}")
    
    def log_message_sent(self, username, room_id, message_length):
        """Log de mensaje enviado"""
        self.logger.info(f"📨 Mensaje enviado | Usuario: {username} | Sala: {room_id} | Longitud: {message_length}")
    
    def log_error(self, event, error, sid=None):
        """Log de error en Socket.IO"""
        sid_info = f"| SID: {sid}" if sid else ""
        self.logger.error(f"❌ Error en evento '{event}' {sid_info} | Error: {error}")

# Instancia global del logger de Socket.IO
socketio_logger = SocketIOLogger()