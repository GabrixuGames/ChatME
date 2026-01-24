from flask import jsonify, render_template, request, send_from_directory


def register_system_routes(app, require_jwt, logger):
    @app.route('/verificar_sesion', methods=['GET', 'OPTIONS'])
    @require_jwt
    def verificar_sesion():
        """Verificar si el usuario tiene sesión activa (JWT)"""
        username = getattr(request, 'username', None)
        if username:
            return jsonify({"authenticated": True, "username": username}), 200
        return jsonify({"authenticated": False}), 401

    @app.route("/")
    def home():
        """Página principal"""
        if logger:
            logger.info("🏠 Acceso a página principal")
        return render_template("index.html")

    @app.route('/favicon.ico')
    def favicon():
        """Servir favicon"""
        return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')
