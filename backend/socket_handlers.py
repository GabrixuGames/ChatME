from flask_socketio import emit, join_room
from flask import request


def register_socket_handlers(socketio, auth_service, chat_service, socketio_logger, logger):
    @socketio.on('connect')
    def handle_connect():
        """Manejar nueva conexión Socket.IO con auto-join a salas del usuario"""
        try:
            socketio_logger.log_connection(request.sid)
            username = request.args.get('username')

            if username:
                join_room(f"user_{username}")
                logger.info(f"👤 {username} unido a sala personal")

                user = auth_service.get_user_by_username(username)
                if user:
                    rooms = chat_service.get_user_rooms(user['id'])
                    for room in rooms:
                        join_room(room['id'])
                        logger.info(f"🏛️ {username} auto-join a sala {room['id']}")

            emit('connected', {"message": "Conectado al servidor"})
        except Exception as e:
            socketio_logger.log_error('connect', e, request.sid)

    @socketio.on('disconnect')
    def handle_disconnect():
        """Manejar desconexión Socket.IO"""
        try:
            from flask import request
            socketio_logger.log_disconnection(request.sid)
        except Exception as e:
            socketio_logger.log_error('disconnect', e, None)

    @socketio.on('join')
    def handle_join(data):
        """Manejar unión a sala con manejo de errores"""
        try:
            if not data or 'room' not in data or 'username' not in data:
                emit('error', {"message": "Datos de sala incompletos"})
                return

            room_id = data['room']
            username = data['username']

            join_room(room_id)
            socketio_logger.log_join_room(request.sid, room_id, username)

            messages = chat_service.get_room_messages(room_id)
            emit('previous_messages', messages)
            logger.info(f"📤 Enviados {len(messages)} mensajes históricos a {username}")

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
        """Manejar envío de mensaje con validación y errores"""
        try:
            if not data or 'username' not in data or 'room' not in data or 'message' not in data:
                emit('error', {"message": "Datos de mensaje incompletos"})
                return

            username = data['username']
            room_id = data['room']
            content = data['message']

            message_result = chat_service.send_message(username, room_id, content)

            if message_result:
                emit('message', message_result, room=room_id)
                socketio_logger.log_message_sent(username, room_id, len(content))
            else:
                emit('error', {"message": "Error al enviar mensaje"})

        except Exception as e:
            socketio_logger.log_error('message', e, request.sid)
            emit('error', {"message": "Error interno al procesar mensaje"})

    @socketio.on('typing')
    def handle_typing(data):
        """Manejar evento de usuario escribiendo"""
        try:
            username = data.get('username')
            room_id = data.get('room')

            if username and room_id:
                emit('user_typing', {'username': username, 'room': room_id},
                     room=room_id, include_self=False)
        except Exception as e:
            socketio_logger.log_error('typing', e, request.sid)

    @socketio.on('stop_typing')
    def handle_stop_typing(data):
        """Manejar evento de usuario dejó de escribir"""
        try:
            username = data.get('username')
            room_id = data.get('room')

            if username and room_id:
                emit('user_stop_typing', {'username': username, 'room': room_id},
                     room=room_id, include_self=False)
        except Exception as e:
            socketio_logger.log_error('stop_typing', e, request.sid)
