from functools import wraps
from flask import request, jsonify, current_app, g
import json

def login_required():
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            session_id = request.cookies.get('session_id')
            if not session_id:
                current_app.logger.error("Acesso negado: session_id ausente.")
                return jsonify({"error": "Acesso negado. 1"}), 403

            try:
                user = current_app.redis_client.get(session_id)
                if not user:
                    current_app.logger.error("Acesso negado: sessão inválida ou expirada.")
                    return jsonify({"error": "Acesso negado. 2"}), 403

                session_data = json.loads(user.decode('utf-8'))
                user_data = session_data.get('user')
                if not user_data:
                    current_app.logger.error("Acesso negado: dados do usuário ausentes na sessão.")
                    return jsonify({"error": "Acesso negado. 3"}), 403
                
                ip = request.remote_addr
                
                user_data.update({
                    'ip': ip
                })
                
                g.user_data = user_data
                
            except Exception as e:
                current_app.logger.error(f"Erro em login_required: {e}")
                return jsonify({"error": "Acesso negado. 4"}), 403

            return func(*args, **kwargs)
        return decorated_function
    return decorator

def role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            # Verifica se g.user_data foi definido pelo login_required
            user_data = getattr(g, 'user_data', None)
            if not user_data:
                current_app.logger.error("Acesso negado: dados do usuário não encontrados. Verifique se 'login_required' está aplicado.")
                return jsonify({"error": "Acesso negado. 5"}), 403

            user_roles = user_data.get('role', [])
            if not any(role in allowed_roles for role in user_roles):
                current_app.logger.error(f"Acesso negado. Role: {user_roles} Allowed: {allowed_roles}")
                return jsonify({"error": "Acesso negado. 6"}), 403

            return func(*args, **kwargs)
        return decorated_function
    return decorator
