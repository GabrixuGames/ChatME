from flask import jsonify, request
import psycopg2.extras


def register_friend_routes(app, require_jwt, socketio, logger, limiter):
    @app.route('/friends/remove', methods=['POST', 'OPTIONS'])
    @require_jwt
    def remove_friend():
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        user_id = getattr(request, 'user_id', None)
        username = getattr(request, 'username', None)
        friend_id = data.get('friend_id')
        if not user_id or not friend_id:
            return jsonify({'error': 'Faltan datos'}), 400

        connection = app.db_manager.get_connection()
        try:
            with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("SELECT username FROM users WHERE id = %s", (friend_id,))
                friend = cursor.fetchone()

                cursor.execute("""
                    SELECT id FROM rooms
                    WHERE room_type = 'individual'
                    AND ((user_id_1 = %s AND user_id_2 = %s) OR (user_id_1 = %s AND user_id_2 = %s))
                """, (user_id, friend_id, friend_id, user_id))
                room = cursor.fetchone()
        finally:
            app.db_manager.return_connection(connection)

        ok = app.friend_service.remove_friend(user_id, friend_id)

        if ok and friend and room:
            logger.info(f"💔 {username} eliminó a {friend['username']} de sus amigos")

            socketio.emit('friendship_ended', {
                'room_id': room['id'],
                'message': 'Ya no sois amigos'
            }, room=f"user_{username}")

            socketio.emit('friendship_ended', {
                'room_id': room['id'],
                'message': 'Ya no sois amigos'
            }, room=f"user_{friend['username']}")

        return jsonify({'success': ok}), 200 if ok else 400

    @app.route('/friends/send_request', methods=['POST', 'OPTIONS'])
    @require_jwt
    def send_friend_request():
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        sender_id = getattr(request, 'user_id', None)
        sender_username = getattr(request, 'username', None)
        receiver_id = data.get('receiver_id')
        if not sender_id or not receiver_id:
            return jsonify({'error': 'Faltan datos'}), 400

        connection = app.db_manager.get_connection()
        try:
            with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("SELECT username FROM users WHERE id = %s", (receiver_id,))
                receiver = cursor.fetchone()
        finally:
            app.db_manager.return_connection(connection)

        req_id = app.friend_service.send_request(sender_id, receiver_id)
        if req_id:
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
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        request_id = data.get('request_id')
        status = data.get('status')
        if not request_id or status not in ['accepted', 'rejected']:
            return jsonify({'error': 'Datos inválidos'}), 400

        connection = app.db_manager.get_connection()
        try:
            with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
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
        finally:
            app.db_manager.return_connection(connection)

        ok = app.friend_service.respond_request(request_id, status)

        if ok and status == 'accepted' and req_info:
            logger.info(f"🎉 Amistad aceptada: {req_info['sender_username']} ↔ {req_info['receiver_username']}")

            logger.info(f"📤 Emitiendo evento a sala: user_{req_info['sender_username']}")
            socketio.emit('friend_request_accepted', {
                'message': f'{req_info["receiver_username"]} aceptó tu solicitud de amistad',
                'friend_username': req_info['receiver_username']
            }, room=f"user_{req_info['sender_username']}")

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
        friends = app.friend_service.get_friends(user_id)
        return jsonify({'friends': friends})

    @app.route('/friends/pending', methods=['GET', 'OPTIONS'])
    @require_jwt
    def list_pending_requests():
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return jsonify({'pending_requests': []})
        pending = app.friend_service.get_pending_requests(user_id)
        return jsonify({'pending_requests': pending})

    @app.route('/friends/sent', methods=['GET', 'OPTIONS'])
    @require_jwt
    def list_sent_requests():
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return jsonify({'sent_requests': []})
        sent = app.friend_service.get_sent_requests(user_id)
        return jsonify({'sent_requests': sent})

    @app.route('/friends/search', methods=['GET', 'OPTIONS'])
    @require_jwt
    @limiter.limit("30 per minute")
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

        friends = app.friend_service.get_friends(user_id)
        exclude_ids = [user_id] + [f['id'] for f in friends]
        logger.info(f"📋 Excluyendo {len(exclude_ids)} usuarios de la búsqueda")

        users = app.friend_service.search_users(query_str, exclude_ids)
        logger.info(f"✅ Encontrados {len(users)} usuarios")
        return jsonify({'users': users})
