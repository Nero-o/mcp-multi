from flask import Blueprint, request, jsonify, current_app
from app.controllers.usuario_controller import UsuarioController
usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route('/create_usuario', methods=['POST'])
def create():
    """
    Cria um novo usuário no sistema.
    
    Payload esperado (JSON):
    {
        "email": string (obrigatório) - Email do usuário que também será usado como username,
        "role": string (obrigatório) - Papel do usuário ("Fornecedor", "Parceiro", "ParceiroAdministrador" ou "Administrador"),
        "nome": string (opcional) - Nome completo do usuário,
        "telefone": string (opcional) - Telefone do usuário,
        
        # Campos obrigatórios apenas para role "Fornecedor":
        "cpf_cnpj": string (condicional) - CPF/CNPJ do fornecedor,
        "razao_social": string (condicional) - Razão social do fornecedor,
        # ... outros campos opcionais do fornecedor ...
    }
    """
    return UsuarioController.create_usuario(request.json)

@usuario_bp.route('/lista_usuario', methods=['GET'])
def get_all():
    """
    Lista todos os usuários com paginação.
    
    Query Parameters:
    - page: integer (opcional, default=1) - Página atual
    - per_page: integer (opcional, default=10) - Itens por página
    
    Headers necessários:
    - tenant-url: string (obrigatório) - URL do tenant para identificar o parceiro
    
    Retornos:
    - 200: Lista de usuários
        {
            "items": [...],
            "total": integer,
            "page": integer,
            "per_page": integer,
            "pages": integer
        }
    - 404: Nenhum usuário encontrado
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    usuarios = UsuarioController.get_all_usuario(page, per_page)
    if usuarios:
        return jsonify(usuarios), 200
    return jsonify({'msg': 'Usuário não encontrado'}), 404

# Rota para obter um usuário específico
@usuario_bp.route('/get_usuario', methods=['GET'])
def get():
    usuario_id = request.args.get('usuario_id')
    usuario = UsuarioController.get_usuario_por_id(usuario_id)
    if usuario:
        return jsonify(usuario.serialize()), 200
    return jsonify({'error': 'Usuário não encontrado'}), 404

# Rota para atualizar um usuário
@usuario_bp.route('/update_usuario', methods=['PUT'])
def update():
    usuario_id = request.args.get('usuario_id')
    dados = request.json
    usuario_atualizado = UsuarioController.update_usuario(usuario_id, dados)
    if usuario_atualizado:
        return jsonify(usuario_atualizado.serialize()), 200
    return jsonify({'error': 'Usuário não encontrado'}), 404

# Rota para deletar um usuário
@usuario_bp.route('/delete_usuario', methods=['DELETE'])
def delete():
    usuario_id = request.args.get('usuario_id')
    if UsuarioController.delete_usuario(usuario_id):
        return jsonify({'msg': 'Usuário deletado com sucesso'}), 200
    return jsonify({'error': 'Usuário não encontrado'}), 404