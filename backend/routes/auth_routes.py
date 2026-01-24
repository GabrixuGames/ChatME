from datetime import datetime, timedelta, timezone
from flask import jsonify, request
import jwt


def register_auth_routes(app, limiter, jwt_secret, logger):
    @app.route('/register', methods=['POST'])
    @limiter.limit("5 per minute")
    def register():
        """Registro de usuario nuevo"""
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

            user_exists = app.auth_service.get_user_by_username(username)
            if user_exists:
                logger.warning(f"❌ Usuario ya existe: {username}")
                return jsonify({"error": "El usuario ya existe"}), 409

            user_id = app.auth_service.register_user(username, email, password)
            if user_id:
                logger.info(f"✅ Usuario registrado: {username}")
                return jsonify({"message": "Registro exitoso", "user_id": user_id}), 201
            logger.error(f"❌ Error al registrar usuario: {username}")
            return jsonify({"error": "No se pudo registrar el usuario"}), 500
        except Exception as e:
            logger.error(f"❌ Error interno en registro: {e}")
            return jsonify({"error": "Error interno del servidor"}), 500

    @app.route('/procesar_login', methods=['POST'])
    @limiter.limit("10 per minute")
    def procesar_login():
        """Procesar login de usuario con manejo de errores profesional"""
        try:
            if not request.is_json:
                logger.warning("❌ Request sin JSON en login")
                return jsonify({"error": "Content-Type debe ser application/json"}), 400

            data = request.get_json()

            if not data or 'username' not in data or 'password' not in data:
                logger.warning("❌ Campos faltantes en login")
                return jsonify({"error": "Username y password son requeridos"}), 400

            username = data.get('username', '').strip()
            password = data.get('password', '')

            if not username or not password:
                logger.warning("❌ Campos vacíos en login")
                return jsonify({"error": "Username y password no pueden estar vacíos"}), 400

            user = app.auth_service.authenticate_user(username, password)

            if user:
                current_time = datetime.now(timezone.utc)
                token_payload = {
                    "user_id": user['id'],
                    "username": user['username'],
                    "iat": current_time,
                    "exp": current_time + timedelta(hours=24),
                    "iss": "chatme-app",
                    "aud": "chatme-users"
                }

                token = jwt.encode(token_payload, jwt_secret, algorithm="HS256")

                logger.info(f"✅ Login exitoso: {username} (token generado)")
                logger.debug(f"🔐 Token info - User: {user['id']}, Expires: {current_time + timedelta(hours=24)}")

                return jsonify({
                    "message": "Login exitoso",
                    "username": user['username'],
                    "token": token,
                    "expires_in": 24 * 60 * 60
                }), 200

            logger.warning(f"❌ Login fallido: {username}")
            return jsonify({"error": "Credenciales incorrectas"}), 401

        except Exception as e:
            logger.error(f"❌ Error interno en login: {e}")
            return jsonify({"error": "Error interno del servidor"}), 500

    @app.route('/logout', methods=['POST'])
    def logout():
        """Cerrar sesión (solo frontend, JWT)"""
        return jsonify({"message": "Logout frontend, borra el token JWT"}), 200
