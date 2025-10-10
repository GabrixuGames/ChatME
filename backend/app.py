"""
Refactored Main Application
Implementa arquitectura en capas con patrones profesionales
"""
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Importar nuestros servicios y middleware
from services.auth_service import AuthService
from services.chat_service import ChatService
from middleware.logging_middleware import setup_logging, log_request_middleware, socketio_logger
from utils.database import db_manager

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logger = setup_logging()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'clave_secreta_cambiar_en_produccion')
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False  # True si usas HTTPS
)

# Configurar CORS
CORS(app, origins="*", supports_credentials=False)

# Configurar Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*")

# Configurar middleware de logging
log_request_middleware(app)

# Inicializar servicios
auth_service = AuthService()
chat_service = ChatService()

# ============================================================================
# RUTAS HTTP
# ============================================================================

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
            # Guardar en sesión
            session['username'] = user['username']
            session['user_id'] = user['id']
            
            logger.info(f"✅ Login exitoso: {username}")
            return jsonify({
                "message": "Login exitoso",
                "username": user['username']
            }), 200
        else:
            logger.warning(f"❌ Login fallido: {username}")
            return jsonify({"error": "Credenciales incorrectas"}), 401
            
    except Exception as e:
        logger.error(f"❌ Error interno en login: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/logout', methods=['POST'])
def logout():
    """Cerrar sesión"""
    try:
        username = session.get('username', 'Unknown')
        session.clear()
        logger.info(f"👋 Logout: {username}")
        return jsonify({"message": "Sesión cerrada"}), 200
    except Exception as e:
        logger.error(f"❌ Error en logout: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/verificar_sesion', methods=['GET'])
def verificar_sesion():
    """Verificar si el usuario tiene sesión activa"""
    try:
        username = session.get('username')
        if username:
            return jsonify({"authenticated": True, "username": username}), 200
        else:
            return jsonify({"authenticated": False}), 401
    except Exception as e:
        logger.error(f"❌ Error verificando sesión: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

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