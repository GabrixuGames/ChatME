
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
import psycopg2.extras

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

# Inicializar servicios
auth_service = AuthService()
chat_service = ChatService()
friend_service = FriendService()

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
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            request.user_id = payload.get('user_id')
            request.username = payload.get('username')
        except Exception as e:
            return jsonify({'error': 'Token JWT inválido'}), 401
        return f(*args, **kwargs)
    return decorated


@app.route('/chat/individual/create', methods=['POST', 'OPTIONS'])
@require_jwt
def create_individual_chat():
    """Crear o recuperar sala individual entre dos usuarios"""
    try:
        data = request.get_json()
        username_1 = getattr(request, 'username', None)
        username_2 = data.get('username_2')
        is_temporary = data.get('is_temporary', False)
        if not username_1 or not username_2:
            return jsonify({'error': 'Faltan datos'}), 400
        room = chat_service.get_or_create_individual_room(username_1, username_2, is_temporary)
        if room:
            # Convertir datetime a string para serialización JSON
            if 'created_at' in room and isinstance(room['created_at'], datetime):
                room['created_at'] = room['created_at'].isoformat()
            
            # Emitir evento Socket.IO para notificar a ambos usuarios
            socketio.emit('new_individual_chat', {
                'room': room,
                'for_user': username_2
            }, room=f"user_{username_2}")
            
            logger.info(f"💬 Chat individual creado: {username_1} ↔ {username_2}, room_id: {room['id']}")
            return jsonify({'room': room}), 200
        return jsonify({'error': 'No se pudo crear sala'}), 500
    except Exception as e:
        logger.error(f"❌ Error interno en create_individual_chat: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/chat/individual/delete', methods=['POST', 'OPTIONS'])
@require_jwt
def delete_individual_chat():
    """Eliminar/desactivar sala individual"""
    data = request.get_json()
    room_id = data.get('room_id')
    if not room_id:
        return jsonify({'error': 'Falta room_id'}), 400
    ok = chat_service.delete_room(room_id)
    return jsonify({'success': ok}), 200 if ok else 400

@app.route('/chat/individual/cleanup_temporary', methods=['POST', 'OPTIONS'])
@require_jwt
def cleanup_temporary_chats():
    """Eliminar todos los chats temporales del usuario (por ejemplo, al cerrar sesión)"""
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        return jsonify({'error': 'Falta user_id'}), 400
    count = chat_service.cleanup_temporary_rooms(user_id)
    return jsonify({'deleted_count': count}), 200

@app.route('/chat/rooms', methods=['GET', 'OPTIONS'])
@require_jwt
def get_rooms():
    """Obtener salas del usuario con información completa"""
    user_id = getattr(request, 'user_id', None)
    username = getattr(request, 'username', None)
    if not user_id:
        return jsonify({'rooms': []})
    
    rooms = chat_service.get_user_rooms_detailed(user_id, username)
    return jsonify({'rooms': rooms})

@app.route('/chat/mark_read', methods=['POST', 'OPTIONS'])
@require_jwt
def mark_messages_read():
    """Marcar mensajes de una sala como leídos"""
    user_id = getattr(request, 'user_id', None)
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
            
        room_id = data.get('room_id')
        
        if not user_id or not room_id:
            return jsonify({'error': 'Faltan datos requeridos'}), 400
        
        count = chat_service.mark_messages_as_read(user_id, room_id)
        return jsonify({'marked_count': count}), 200
    except Exception as e:
        logger.error(f"❌ Error en mark_messages_read: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/chat/hide_room', methods=['POST', 'OPTIONS'])
@require_jwt
def hide_chat_room():
    """Ocultar sala para el usuario"""
    user_id = getattr(request, 'user_id', None)
    data = request.get_json()
    room_id = data.get('room_id')
    
    if not user_id or not room_id:
        return jsonify({'error': 'Faltan datos'}), 400
    
    success = chat_service.hide_room(user_id, room_id)
    return jsonify({'success': success}), 200 if success else 400

@app.route('/friends/remove', methods=['POST', 'OPTIONS'])
@require_jwt
def remove_friend():
    data = request.get_json()
    user_id = getattr(request, 'user_id', None)
    friend_id = data.get('friend_id')
    if not user_id or not friend_id:
        return jsonify({'error': 'Faltan datos'}), 400
    ok = friend_service.remove_friend(user_id, friend_id)
    return jsonify({'success': ok}), 200 if ok else 400

@app.route('/friends/send_request', methods=['POST', 'OPTIONS'])
@require_jwt
def send_friend_request():
    data = request.get_json()
    sender_id = getattr(request, 'user_id', None)
    sender_username = getattr(request, 'username', None)
    receiver_id = data.get('receiver_id')
    if not sender_id or not receiver_id:
        return jsonify({'error': 'Faltan datos'}), 400
    
    # Obtener username del receptor
    connection = db_manager.get_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT username FROM users WHERE id = %s", (receiver_id,))
    receiver = cursor.fetchone()
    db_manager.return_connection(connection)
    
    req_id = friend_service.send_request(sender_id, receiver_id)
    if req_id:
        # Notificar al receptor en tiempo real si está conectado
        if receiver:
            logger.info(f"📬 Solicitud enviada: {sender_username} → {receiver['username']}")
            logger.info(f"📤 Emitiendo evento a sala: user_{receiver['username']}")
            socketio.emit('friend_request_received', {
                'message': f'{sender_username} te envió una solicitud de amistad',
                'sender_username': sender_username,
                'request_id': req_id
            }, room=f"user_{receiver['username']}")
        
        return jsonify({'message': 'Solicitud enviada', 'request_id': req_id}), 200
    return jsonify({'error': 'No se pudo enviar solicitud'}), 400

@app.route('/friends/respond_request', methods=['POST', 'OPTIONS'])
@require_jwt
def respond_friend_request():
    data = request.get_json()
    request_id = data.get('request_id')
    status = data.get('status')
    if not request_id or status not in ['accepted', 'rejected']:
        return jsonify({'error': 'Datos inválidos'}), 400
    
    # Obtener información de la solicitud antes de responder
    connection = db_manager.get_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("""
        SELECT fr.sender_id, fr.receiver_id, 
               u1.username as sender_username, 
               u2.username as receiver_username
        FROM friend_requests fr
        JOIN users u1 ON fr.sender_id = u1.id
        JOIN users u2 ON fr.receiver_id = u2.id
        WHERE fr.id = %s
    """, (request_id,))
    req_info = cursor.fetchone()
    db_manager.return_connection(connection)
    
    ok = friend_service.respond_request(request_id, status)
    
    # Si se aceptó la solicitud, notificar a ambos usuarios vía Socket.IO
    if ok and status == 'accepted' and req_info:
        logger.info(f"🎉 Amistad aceptada: {req_info['sender_username']} ↔ {req_info['receiver_username']}")
        
        # Notificar al que envió la solicitud
        logger.info(f"📤 Emitiendo evento a sala: user_{req_info['sender_username']}")
        socketio.emit('friend_request_accepted', {
            'message': f'{req_info["receiver_username"]} aceptó tu solicitud de amistad',
            'friend_username': req_info['receiver_username']
        }, room=f"user_{req_info['sender_username']}")
        
        # Notificar al que aceptó (opcional, pero útil para confirmar)
        logger.info(f"📤 Emitiendo evento a sala: user_{req_info['receiver_username']}")
        socketio.emit('friend_request_accepted', {
            'message': f'Ahora eres amigo de {req_info["sender_username"]}',
            'friend_username': req_info['sender_username']
        }, room=f"user_{req_info['receiver_username']}")
    
    return jsonify({'success': ok}), 200 if ok else 400

@app.route('/friends/list', methods=['GET', 'OPTIONS'])
@require_jwt
def list_friends():
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        return jsonify({'friends': []})
    friends = friend_service.get_friends(user_id)
    return jsonify({'friends': friends})

@app.route('/friends/pending', methods=['GET', 'OPTIONS'])
@require_jwt
def list_pending_requests():
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        return jsonify({'pending_requests': []})
    pending = friend_service.get_pending_requests(user_id)
    return jsonify({'pending_requests': pending})

    

@app.route('/friends/sent', methods=['GET', 'OPTIONS'])
@require_jwt
def list_sent_requests():
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        return jsonify({'sent_requests': []})
    sent = friend_service.get_sent_requests(user_id)
    return jsonify({'sent_requests': sent})

    

@app.route('/friends/search', methods=['GET', 'OPTIONS'])
@require_jwt
def search_users():
    user_id = getattr(request, 'user_id', None)
    query_str = request.args.get('query', '').strip()
    logger.info(f"🔎 Búsqueda de amigos: user_id={user_id}, query='{query_str}'")
    
    if not user_id:
        logger.warning("❌ Búsqueda sin user_id")
        return jsonify({'users': [], 'error': 'Usuario no autenticado'}), 401
    
    if not query_str or len(query_str) < 3:
        logger.warning(f"⚠️ Query muy corto: '{query_str}'")
        return jsonify({'users': []})
    
    # Excluir el propio usuario y amigos actuales
    friends = friend_service.get_friends(user_id)
    exclude_ids = [user_id] + [f['id'] for f in friends]
    logger.info(f"📋 Excluyendo {len(exclude_ids)} usuarios de la búsqueda")
    
    users = friend_service.search_users(query_str, exclude_ids)
    logger.info(f"✅ Encontrados {len(users)} usuarios")
    return jsonify({'users': users})

    

@app.route('/verificar_sesion', methods=['GET', 'OPTIONS'])
@require_jwt
def verificar_sesion():
    """Verificar si el usuario tiene sesión activa (JWT)"""
    username = getattr(request, 'username', None)
    if username:
        return jsonify({"authenticated": True, "username": username}), 200
    else:
        return jsonify({"authenticated": False}), 401

    



## --- ENDPOINTS SISTEMA DE AMIGOS --- ##

# Endpoint de registro de usuario
@app.route('/register', methods=['POST'])
def register():
    """
    Registro de usuario nuevo
    """
    try:
        if not request.is_json:
            logger.warning("❌ Request sin JSON en registro")
            return jsonify({"error": "Content-Type debe ser application/json"}), 400

        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not username or not email or not password:
            logger.warning("❌ Campos faltantes en registro")
            return jsonify({"error": "Todos los campos son requeridos"}), 400

        # Verificar si el usuario ya existe
        user_exists = auth_service.get_user_by_username(username)
        if user_exists:
            logger.warning(f"❌ Usuario ya existe: {username}")
            return jsonify({"error": "El usuario ya existe"}), 409

        # Crear usuario usando AuthService
        user_id = auth_service.register_user(username, email, password)
        if user_id:
            logger.info(f"✅ Usuario registrado: {username}")
            return jsonify({"message": "Registro exitoso", "user_id": user_id}), 201
        else:
            logger.error(f"❌ Error al registrar usuario: {username}")
            return jsonify({"error": "No se pudo registrar el usuario"}), 500
    except Exception as e:
        logger.error(f"❌ Error interno en registro: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500








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


# ============================================================================
# EVENTOS SOCKET.IO
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Manejar nueva conexión Socket.IO con auto-join a salas del usuario"""
    try:
        socketio_logger.log_connection(request.sid)
        
        # Obtener username desde query params o headers
        username = request.args.get('username')
        
        if username:
            # Unir a sala personal del usuario (para notificaciones)
            from flask_socketio import join_room as socketio_join
            socketio_join(f"user_{username}")
            logger.info(f"👤 {username} unido a sala personal")
            
            # Obtener user_id
            user = auth_service.get_user_by_username(username)
            if user:
                # Auto-join a todas las salas del usuario
                rooms = chat_service.get_user_rooms(user['id'])
                for room in rooms:
                    socketio_join(room['id'])
                    logger.info(f"🏛️ {username} auto-join a sala {room['id']}")
        
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

@socketio.on('typing')
def handle_typing(data):
    """
    Manejar evento de usuario escribiendo
    """
    try:
        username = data.get('username')
        room_id = data.get('room')
        
        if username and room_id:
            # Emitir a todos en la sala excepto el remitente
            emit('user_typing', {'username': username, 'room': room_id}, 
                 room=room_id, include_self=False)
    except Exception as e:
        socketio_logger.log_error('typing', e, request.sid)

@socketio.on('stop_typing')
def handle_stop_typing(data):
    """
    Manejar evento de usuario dejó de escribir
    """
    try:
        username = data.get('username')
        room_id = data.get('room')
        
        if username and room_id:
            # Emitir a todos en la sala excepto el remitente
            emit('user_stop_typing', {'username': username, 'room': room_id}, 
                 room=room_id, include_self=False)
    except Exception as e:
        socketio_logger.log_error('stop_typing', e, request.sid)

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