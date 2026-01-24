
"""
Refactored Main Application
Implementa arquitectura en capas con patrones profesionales
"""
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import jwt
from functools import wraps
from dotenv import load_dotenv

# Importar nuestros servicios y middleware
from services.auth_service import AuthService
from services.chat_service import ChatService
from services.friend_service import FriendService
from middleware.logging_middleware import setup_logging, log_request_middleware, socketio_logger
from utils.database import db_manager
from routes.chat_routes import register_chat_routes
from routes.friend_routes import register_friend_routes
from routes.auth_routes import register_auth_routes
from routes.system_routes import register_system_routes
from socket_handlers import register_socket_handlers

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logger = setup_logging()

# Validar configuración crítica de seguridad
def validate_security_config():
    """Validar que las configuraciones críticas estén presentes"""
    
    # Validar JWT Secret - requerido sin defaults
    jwt_secret = os.getenv('JWT_SECRET')
    if not jwt_secret:
        raise ValueError(
            "❌ CRITICAL ERROR: JWT_SECRET environment variable is required!\n"
            "Set JWT_SECRET with a strong, random secret (min 32 characters):\n"
            "export JWT_SECRET='your-super-secure-random-jwt-secret-key-here'"
        )
    
    if len(jwt_secret) < 32:
        raise ValueError(
            "❌ CRITICAL ERROR: JWT_SECRET must be at least 32 characters long!\n"
            f"Current length: {len(jwt_secret)} characters"
        )
    
    # Validar Flask Secret Key - requerido sin defaults
    flask_secret = os.getenv('FLASK_SECRET_KEY')
    if not flask_secret:
        raise ValueError(
            "❌ CRITICAL ERROR: FLASK_SECRET_KEY environment variable is required!\n"
            "Set FLASK_SECRET_KEY with a strong, random secret (min 32 characters):\n"
            "export FLASK_SECRET_KEY='your-super-secure-flask-secret-key-here'"
        )
    
    if len(flask_secret) < 32:
        raise ValueError(
            "❌ CRITICAL ERROR: FLASK_SECRET_KEY must be at least 32 characters long!\n"
            f"Current length: {len(flask_secret)} characters"
        )
    
    # Validar configuración de entorno
    environment = os.getenv('ENVIRONMENT', 'development').lower()
    
    return {
        'jwt_secret': jwt_secret,
        'flask_secret': flask_secret,
        'environment': environment
    }

app = Flask(__name__)

# Validar y obtener configuración segura
try:
    security_config = validate_security_config()
    jwt_secret = security_config['jwt_secret']
    environment = security_config['environment']
    
    app.secret_key = security_config['flask_secret']
    
    # Configuración de cookies según entorno
    if environment == 'production':
        app.config.update(
            SESSION_COOKIE_SAMESITE='Strict',
            SESSION_COOKIE_SECURE=True,
            SESSION_COOKIE_HTTPONLY=True,
            PERMANENT_SESSION_LIFETIME=3600  # 1 hora
        )
    else:
        app.config.update(
            SESSION_COOKIE_SAMESITE='Lax',
            SESSION_COOKIE_SECURE=False,  # Desarrollo local
            SESSION_COOKIE_HTTPONLY=True
        )
        
    logger.info(f"✅ Security configuration loaded for {environment} environment")

except ValueError as e:
    logger.error(str(e))
    raise  # Detener la aplicación si la configuración es inválida

# Configurar Rate Limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Configurar CORS - permitir credenciales y configurar orígenes específicos
allowed_origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://172.20.10.10:8080",
    "http://192.168.56.1:8080",
    "http://172.24.144.1:8080"
]

CORS(app, 
     origins=allowed_origins, 
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     expose_headers=["Content-Type", "Authorization"])

# Configurar Socket.IO
socketio = SocketIO(app, 
                   cors_allowed_origins=allowed_origins,
                   cors_credentials=True)

# Configurar middleware de logging
log_request_middleware(app)

# Proxy para permitir mocks en tests sin romper el acceso desde rutas
class ServiceProxy:
    def __init__(self, getter):
        self._getter = getter

    def __getattr__(self, name):
        return getattr(self._getter(), name)

# Inicializar servicios
auth_service = AuthService()
chat_service = ChatService()
friend_service = FriendService()
app.auth_service = ServiceProxy(lambda: auth_service)
app.chat_service = ServiceProxy(lambda: chat_service)
app.friend_service = ServiceProxy(lambda: friend_service)
app.db_manager = db_manager

# --- JWT DECORATOR (must be above endpoints that use it) --- #
def require_jwt(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Permitir peticiones OPTIONS sin JWT (para CORS preflight)
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
        
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token JWT requerido'}), 401
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(
                token, 
                jwt_secret, 
                algorithms=["HS256"],
                audience="chatme-users",
                issuer="chatme-app",
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True
                }
            )
            
            # Validar estructura del payload
            user_id = payload.get('user_id')
            username = payload.get('username')
            issuer = payload.get('iss')
            audience = payload.get('aud')
            
            if not user_id or not username:
                logger.warning(f"🚨 JWT payload inválido: missing user_id or username")
                return jsonify({'error': 'Token JWT inválido - estructura incorrecta'}), 401
            
            if issuer != 'chatme-app':
                logger.warning(f"🚨 JWT issuer inválido: {issuer}")
                return jsonify({'error': 'Token JWT inválido - issuer incorrecto'}), 401
                
            if audience != 'chatme-users':
                logger.warning(f"🚨 JWT audience inválido: {audience}")
                return jsonify({'error': 'Token JWT inválido - audience incorrecto'}), 401
            
            request.user_id = user_id
            request.username = username
            request.jwt_payload = payload
            
            logger.debug(f"🔐 JWT validado para usuario: {username} (exp: {payload.get('exp')})")
            
        except jwt.ExpiredSignatureError:
            logger.warning("🚨 Intento de acceso con token JWT expirado")
            return jsonify({'error': 'Token JWT expirado'}), 401
        except jwt.InvalidTokenError as e:
            logger.warning(f"🚨 Intento de acceso con token JWT inválido: {str(e)}")
            return jsonify({'error': 'Token JWT inválido'}), 401
        except Exception as e:
            logger.error(f"❌ Error inesperado validando JWT: {str(e)}")
            return jsonify({'error': 'Error de autenticación'}), 401
        return f(*args, **kwargs)
    return decorated



register_chat_routes(app, require_jwt, socketio, logger)
register_friend_routes(app, require_jwt, socketio, logger, limiter)
register_auth_routes(app, limiter, jwt_secret, logger)
register_system_routes(app, require_jwt, logger)
register_socket_handlers(socketio, auth_service, chat_service, socketio_logger, logger)

# ============================================================================
# UTILIDADES
# ============================================================================

@app.after_request
def add_cache_control(response):
    """Evitar cache en el navegador"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.before_request
def handle_preflight():
    """Manejar peticiones OPTIONS (CORS preflight) antes de cualquier otra lógica"""
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        return response

# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    try:
        logger.info("🚀 Iniciando ChatApp con arquitectura mejorada...")
        logger.info("📊 Connection pool inicializado")
        logger.info("🏗️ Servicios y repositorios cargados")
        
        socketio.run(
            app, 
            host="0.0.0.0", 
            port=5000, 
            debug=True, 
            allow_unsafe_werkzeug=True
        )
    except Exception as e:
        logger.error(f"❌ Error fatal iniciando aplicación: {e}")
    finally:
        # Limpiar recursos
        db_manager.close_all_connections()
        logger.info("🔒 Aplicación cerrada correctamente")
