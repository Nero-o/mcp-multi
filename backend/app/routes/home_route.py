# app/routes/main_routes.py

from flask import Blueprint, g, request, jsonify
from app.services.redis_service import RedisService
from app.utils.decorators import login_required
from app.controllers.home_controller import home_redirect

home_bp = Blueprint('main_bp', __name__)

@home_bp.route('/dashboard', methods=['GET'])
@login_required()
def home():
    session_id = request.cookies.get('session_id')

    if not session_id:
        return jsonify({'error': 'Sessão não encontrada.'}), 401

    usuario_logado = g.user_data
    tenant_url = g.tenant_url
    
    session_data = RedisService.get_session(session_id)

    return home_redirect(usuario_logado, session_data, tenant_url)
