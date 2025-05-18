from flask import Blueprint, request, jsonify, g
from app.utils.decorators import login_required, role_required
from app.controllers.fornecedor_controller import FornecedorController
from app.controllers.auth_controller import AuthController

fornecedor_bp = Blueprint('fornecedor', __name__)

@fornecedor_bp.route('/select-fornecedor-login', methods=['POST'])
@login_required()
@role_required(['Fornecedor'])
def select_fornecedor_login():
    # Get the session_id from cookies
    session_id = request.cookies.get('session_id')
    if not session_id:
        return jsonify({'error': 'Sessão não encontrada.'}), 401
    # Get the selected fornecedor from the request body
    data = request.args.to_dict()
    selected_fornecedor_id = data.get('fornecedor_id')
    if not selected_fornecedor_id:
        return jsonify({'error': 'Nenhum fornecedor selecionado.'}), 400
    
    response = AuthController.select_fornecedor_login(session_id, selected_fornecedor_id, g.tenant_url)

    return response

# Rota para get_all todos os fornecedores
@fornecedor_bp.route('/lista_fornecedor', methods=['GET'])
@login_required()
@role_required(['Administrador', 'ParceiroAdministrador', 'Parceiro'])
def get_all():
    usuario_logado = g.user_data

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    fornecedores = FornecedorController.get_all_fornecedor(page, per_page, usuario_logado, g.tenant_url)

    return jsonify(fornecedores), 200

# Rota para obter um fornecedor específico
@fornecedor_bp.route('/detalhe_fornecedor', methods=['GET'])
@login_required()
# @role_required(['Administrador', 'ParceiroAdministrador', 'Parceiro', 'Fornecedor'])
def obter():
    fornecedor_id = request.args.get('fornecedor_id', type=int)
    if not fornecedor_id:
        return jsonify({'error': 'Requisição inválida.'}), 400
    
    fornecedor = FornecedorController.get_fornecedor_por_id(fornecedor_id)

    if fornecedor:
        return jsonify(fornecedor.serialize()), 200
    
    return jsonify({'error': 'Fornecedor não encontrado'}), 404


# Rota para atualizar um fornecedor
@fornecedor_bp.route('/update_fornecedor', methods=['PUT'])
@login_required()
def atualizar():
    dados = request.json
    fornecedor_id = request.args.get('fornecedor_id')

    if not fornecedor_id:
        return jsonify({'error': 'Requisição inválida. 1'}), 400
    
    response, status_code = FornecedorController.update_fornecedor(fornecedor_id, dados)
    
    return response, status_code