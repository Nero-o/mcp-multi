from flask import request, Blueprint, jsonify, g, current_app # type: ignore
from app.controllers.auth_controller import AuthController
from app.services.redis_service import RedisService
from app.utils.decorators import login_required, role_required

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    senha = data.get('password')
    tenant_url = g.tenant_url

    response = AuthController.auth_login(username, senha, tenant_url)

    return response


@auth_bp.route('/logout', methods=['POST'])
@login_required()
def logout():
    session_id = request.cookies.get('session_id')
    if not session_id:
        return jsonify({'msg': 'Usuário não está logado.'}), 401

    response_auth = AuthController.logout(session_id)

    return response_auth



@auth_bp.route('/alterar-senha-usuario', methods=['POST'])
@login_required()
def alterar_senha_usuario():
    data = request.get_json()
    
    senha_atual = data.get('senha_atual')
    nova_senha = data.get('nova_senha')

    if not senha_atual or not nova_senha:
        return jsonify({"error": "Senha atual e nova senha são obrigatórias."}), 400

    response = AuthController.alterar_senha_usuario(senha_atual, nova_senha)

    return response


@auth_bp.route('/alterar-senha', methods=['POST'])
def alterar_senha_temporaria():
    data = request.json

    # Obtém o temp_session_id do cookie
    temp_session_id = request.cookies.get('temp_session_id')
    if not temp_session_id:
        return jsonify({"error": "Sessão temporária não encontrada."}), 400

    # Recupera os dados da sessão temporária do Redis
    temp_session_data = RedisService.get_session(temp_session_id)
    if not temp_session_data:
        return jsonify({"error": "Sessão temporária inválida ou expirada."}), 400

    email = temp_session_data.get('email')
    session = temp_session_data.get('session')

    # Obtém a nova senha do corpo da requisição
    senha = data.get('new_password')
    if not senha:
        return jsonify({"error": "Nova senha não fornecida."}), 400
    
    response, status_code = AuthController.new_password_challenge(email, senha, session)
    
    # Remove a sessão temporária do Redis e o cookie
    RedisService.delete_session(temp_session_id)
    response.set_cookie('temp_session_id', '', expires=0)

    return response, status_code 


@auth_bp.route('/reset-senha-esquecida', methods=['POST'])
def reset_password_with_code():
    data = request.get_json()
    
    email = data.get('email')
    codigo = data.get('codigo')
    nova_senha = data.get('senha')

    if not email or not codigo or not nova_senha:
        return jsonify({"error": "Email, código de confirmação e nova senha são obrigatórios"}), 400

    response = AuthController.reset_password_with_code(email, codigo, nova_senha)
    return response

@auth_bp.route('/esqueci-senha', methods=['POST'])
def esqueci_senha():

    data = request.get_json()
    if not data:
        return {"error": "Requisição inválida."}, 400
    
    email = data.get('email')
    if not email:
        return {"error": "Requisição inválida."}, 400 
            
    response = AuthController.forgot_password(email)

    return response


@auth_bp.route('/get-user', methods=['GET'])
@login_required()
def get_session_data():
    session_id = request.cookies.get('session_id')
    if not session_id:
        return jsonify({'error': 'Sessão não encontrada.'}), 401

    session_data = RedisService.get_session(session_id)

    if not session_data:
        return jsonify({'error': 'Dados da sessão não encontrados.'}), 401
    
    logged_user_info = session_data['user']

    return jsonify(logged_user_info), 200

