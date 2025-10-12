
"""
Refactored Main Application
Implementa arquitectura en capas con patrones profesionales
"""
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS
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

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logger = setup_logging()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'clave_secreta_cambiar_en_produccion')
jwt_secret = os.getenv('JWT_SECRET', 'jwt_secret_dev')
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False  # Solo para desarrollo local, usar True en producción con HTTPS
)

# Configurar CORS - permitir credenciales y configurar orígenes específicos
allowed_origins = [
    "http://localhost:8080",
    "http://172.20.10.10:8080",
    "http://192.168.56.1:8080",
    "http://172.24.144.1:8080"
]

CORS(app, 
     origins=allowed_origins, 
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS"])

# Configurar Socket.IO
socketio = SocketIO(app, 
                   cors_allowed_origins=allowed_origins,
                   cors_credentials=True)

# Configurar middleware de logging
log_request_middleware(app)

# Inicializar servicios
auth_service = AuthService()
chat_service = ChatService()
friend_service = FriendService()

## --- ENDPOINTS SISTEMA DE AMIGOS --- ##

def require_jwt(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token JWT requerido'}), 401
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            request.user_id = payload.get('user_id')
            request.username = payload.get('username')
        except Exception as e:
            return jsonify({'error': 'Token JWT inválido'}), 401
        return f(*args, **kwargs)
    return decorated

# Eliminar amigo
@app.route('/friends/remove', methods=['POST'])
@require_jwt
def remove_friend():
    data = request.get_json()
    user_id = getattr(request, 'user_id', None)
    friend_id = data.get('friend_id')
    if not user_id or not friend_id:
        return jsonify({'error': 'Faltan datos'}), 400
    ok = friend_service.remove_friend(user_id, friend_id)
    return jsonify({'success': ok}), 200 if ok else 400

# Enviar solicitud de amistad
@app.route('/friends/send_request', methods=['POST'])
@require_jwt
def send_friend_request():
    data = request.get_json()
    sender_id = getattr(request, 'user_id', None)
    receiver_id = data.get('receiver_id')
    if not sender_id or not receiver_id:
        return jsonify({'error': 'Faltan datos'}), 400
    req_id = friend_service.send_request(sender_id, receiver_id)
    if req_id:
        return jsonify({'message': 'Solicitud enviada', 'request_id': req_id}), 200
    return jsonify({'error': 'No se pudo enviar solicitud'}), 400

# Responder solicitud de amistad
@app.route('/friends/respond_request', methods=['POST'])
@require_jwt
def respond_friend_request():
    data = request.get_json()
    request_id = data.get('request_id')
    status = data.get('status')
    if not request_id or status not in ['accepted', 'rejected']:
        return jsonify({'error': 'Datos inválidos'}), 400
    ok = friend_service.respond_request(request_id, status)
    return jsonify({'success': ok}), 200 if ok else 400

# Listar amigos
@app.route('/friends/list', methods=['GET'])
@require_jwt
def list_friends():
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        return jsonify({'friends': []})
    friends = friend_service.get_friends(user_id)
    return jsonify({'friends': friends})

# Listar solicitudes pendientes
@app.route('/friends/pending', methods=['GET'])
@require_jwt
def list_pending_requests():
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        return jsonify({'pending_requests': []})
    pending = friend_service.get_pending_requests(user_id)
    return jsonify({'pending_requests': pending})

# Listar solicitudes enviadas
@app.route('/friends/sent', methods=['GET'])
@require_jwt
def list_sent_requests():
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        return jsonify({'sent_requests': []})
    sent = friend_service.get_sent_requests(user_id)
    return jsonify({'sent_requests': sent})

# Buscar usuarios para añadir amigos
@app.route('/friends/search', methods=['GET'])
@require_jwt
def search_users():
    user_id = getattr(request, 'user_id', None)
    query_str = request.args.get('query', '').strip()
    print(f"🔎 Busqueda de amigos: user_id={user_id}, query='{query_str}'")
    if not user_id or not query_str or len(query_str) < 3:
        return jsonify({'users': []})
    # Excluir el propio usuario y amigos actuales
    friends = friend_service.get_friends(user_id)
    exclude_ids = [user_id] + [f['id'] for f in friends]
    users = friend_service.search_users(query_str, exclude_ids)
    return jsonify({'users': users})

@app.route("/")
def home():
    """Página principal"""
    logger.info("🏠 Acceso a página principal")
    return render_template("index.html")

@app.route('/procesar_login', methods=['POST'])
def procesar_login():
    """
    Procesar login de usuario con manejo de errores profesional
    """
    try:
        # Validar que hay datos JSON
        if not request.is_json:
            logger.warning("❌ Request sin JSON en login")
            return jsonify({"error": "Content-Type debe ser application/json"}), 400
        
        data = request.get_json()
        
        # Validar campos requeridos
        if not data or 'username' not in data or 'password' not in data:
            logger.warning("❌ Campos faltantes en login")
            return jsonify({"error": "Username y password son requeridos"}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Validar que no estén vacíos
        if not username or not password:
            logger.warning("❌ Campos vacíos en login")
            return jsonify({"error": "Username y password no pueden estar vacíos"}), 400
        
        # Intentar autenticar
        user = auth_service.authenticate_user(username, password)
        
        if user:
            # Generar JWT
            token = jwt.encode({
                "user_id": user['id'],
                "username": user['username']
            }, jwt_secret, algorithm="HS256")
            logger.info(f"✅ Login exitoso: {username}")
            return jsonify({
                "message": "Login exitoso",
                "username": user['username'],
                "token": token
            }), 200
        else:
            logger.warning(f"❌ Login fallido: {username}")
            return jsonify({"error": "Credenciales incorrectas"}), 401
            
    except Exception as e:
        logger.error(f"❌ Error interno en login: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/logout', methods=['POST'])
def logout():
    """Cerrar sesión (solo frontend, JWT)"""
    return jsonify({"message": "Logout frontend, borra el token JWT"}), 200

@app.route('/verificar_sesion', methods=['GET'])
@require_jwt
def verificar_sesion():
    """Verificar si el usuario tiene sesión activa (JWT)"""
    username = getattr(request, 'username', None)
    if username:
        return jsonify({"authenticated": True, "username": username}), 200
    else:
        return jsonify({"authenticated": False}), 401

# ============================================================================
# EVENTOS SOCKET.IO
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Manejar nueva conexión Socket.IO"""
    try:
        socketio_logger.log_connection(request.sid)
        emit('connected', {"message": "Conectado al servidor"})
    except Exception as e:
        socketio_logger.log_error('connect', e, request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    """Manejar desconexión Socket.IO"""
    try:
        socketio_logger.log_disconnection(request.sid)
    except Exception as e:
        socketio_logger.log_error('disconnect', e, request.sid)

@socketio.on('join')
def handle_join(data):
    """
    Manejar unión a sala con manejo de errores
    """
    try:
        # Validar datos
        if not data or 'room' not in data or 'username' not in data:
            emit('error', {"message": "Datos de sala incompletos"})
            return
        
        room_id = data['room']
        username = data['username']
        
        # Unirse a la sala Socket.IO
        join_room(room_id)
        socketio_logger.log_join_room(request.sid, room_id, username)
        
        # Obtener mensajes históricos usando el servicio
        messages = chat_service.get_room_messages(room_id)
        
        # Enviar mensajes históricos
        emit('previous_messages', messages)
        logger.info(f"📤 Enviados {len(messages)} mensajes históricos a {username}")
        
        # Notificar a otros usuarios
        emit('user_joined', {
            "message": f"{username} se ha unido a la sala",
            "username": username,
            "roomId": room_id
        }, room=room_id, include_self=False)
        
    except Exception as e:
        socketio_logger.log_error('join', e, request.sid)
        emit('error', {"message": "Error al unirse a la sala"})

@socketio.on('message')
def handle_message(data):
    """
    Manejar envío de mensaje con validación y errores
    """
    try:
        # Validar datos requeridos
        if not data or 'username' not in data or 'room' not in data or 'message' not in data:
            emit('error', {"message": "Datos de mensaje incompletos"})
            return
        
        username = data['username']
        room_id = data['room']
        content = data['message']
        
        # Usar el servicio para enviar el mensaje
        message_result = chat_service.send_message(username, room_id, content)
        
        if message_result:
            # Broadcast a toda la sala
            emit('message', message_result, room=room_id)
            socketio_logger.log_message_sent(username, room_id, len(content))
        else:
            emit('error', {"message": "Error al enviar mensaje"})
            
    except Exception as e:
        socketio_logger.log_error('message', e, request.sid)
        emit('error', {"message": "Error interno al procesar mensaje"})

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

@app.route('/favicon.ico')
def favicon():
    """Servir favicon"""
    from flask import send_from_directory
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

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