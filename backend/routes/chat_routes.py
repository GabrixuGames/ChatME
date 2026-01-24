from datetime import datetime
from flask import jsonify, request


def register_chat_routes(app, require_jwt, socketio, logger):
    @app.route('/chat/individual/create', methods=['POST', 'OPTIONS'])
    @require_jwt
    def create_individual_chat():
        """Crear o recuperar sala individual entre dos usuarios"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No se recibieron datos'}), 400
            username_1 = getattr(request, 'username', None)
            username_2 = data.get('username_2')
            is_temporary = data.get('is_temporary', False)
            if not username_1 or not username_2:
                return jsonify({'error': 'Faltan datos'}), 400
            room = app.chat_service.get_or_create_individual_room(username_1, username_2, is_temporary)
            if room:
                if 'created_at' in room and isinstance(room['created_at'], datetime):
                    room['created_at'] = room['created_at'].isoformat()

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
        user_id = getattr(request, 'user_id', None)
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        room_id = data.get('room_id')

        if not room_id:
            return jsonify({'error': 'Falta room_id'}), 400

        if len(str(room_id)) < 32:
            return jsonify({'error': 'room_id inválido'}), 400

        if not app.chat_service.is_user_in_room(user_id, room_id):
            logger.warning(f"🚨 Usuario {user_id} intentó eliminar room {room_id} sin autorización")
            return jsonify({'error': 'No autorizado'}), 403

        ok = app.chat_service.delete_room(room_id)
        return jsonify({'success': ok}), 200 if ok else 400

    @app.route('/chat/individual/cleanup_temporary', methods=['POST', 'OPTIONS'])
    @require_jwt
    def cleanup_temporary_chats():
        """Eliminar todos los chats temporales del usuario (por ejemplo, al cerrar sesión)"""
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return jsonify({'error': 'Falta user_id'}), 400
        count = app.chat_service.cleanup_temporary_rooms(user_id)
        return jsonify({'deleted_count': count}), 200

    @app.route('/chat/rooms', methods=['GET', 'OPTIONS'])
    @require_jwt
    def get_rooms():
        """Obtener salas del usuario con información completa"""
        user_id = getattr(request, 'user_id', None)
        username = getattr(request, 'username', None)
        if not user_id:
            return jsonify({'rooms': []})

        rooms = app.chat_service.get_user_rooms_detailed(user_id, username)
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

            count = app.chat_service.mark_messages_as_read(user_id, room_id)
            return jsonify({'marked_count': count}), 200
        except Exception as e:
            logger.error(f"❌ Error en mark_messages_read: {e}")
            return jsonify({'error': 'Error interno del servidor'}), 500

    @app.route('/chat/hide_room', methods=['POST', 'OPTIONS'])
    @require_jwt
    def hide_chat_room():
        """Ocultar sala para el usuario y eliminar permanentemente si ambos la ocultaron"""
        try:
            user_id = getattr(request, 'user_id', None)
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No se recibieron datos'}), 400

            room_id = data.get('room_id')

            if not user_id or not room_id:
                return jsonify({'error': 'Faltan datos'}), 400

            room = app.chat_service.get_room_by_id(room_id)
            if not room:
                return jsonify({'error': 'Sala no encontrada'}), 404

            if not app.chat_service.is_user_in_room(user_id, room_id):
                logger.warning(f"🚨 Usuario {user_id} intentó ocultar room {room_id} sin autorización")
                return jsonify({'error': 'No autorizado'}), 403

            success = app.chat_service.hide_room(user_id, room_id)

            if success and room.get('room_type') == 'individual':
                visible_count = app.chat_service.get_visible_users_count(room_id)
                if visible_count == 0:
                    logger.info(f"🗑️ Ambos usuarios ocultaron el room {room_id}, eliminando permanentemente...")
                    app.chat_service.delete_room_permanently(room_id)

            return jsonify({'success': success}), 200 if success else 400

        except Exception as e:
            logger.error(f"❌ Error en hide_chat_room: {e}", exc_info=True)
            return jsonify({'error': 'Error interno del servidor'}), 500
