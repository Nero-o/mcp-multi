from flask import Blueprint,  jsonify, render_template, g, current_app, request # type: ignore
from app.controllers.assinatura_contrato_fornecedor_controller import AssinaturaContratoFornecedor
from app.controllers.fornecedor_controller import FornecedorController
from app.utils.decorators import login_required, role_required

assinatura_contrato_bp = Blueprint('assinatura_contrato', __name__) 

@assinatura_contrato_bp.route('/get-contrato', methods=['GET'])
@login_required()
@role_required(['Fornecedor'])
def get_contrato():
    fornecedor_id = g.user_data.get('fornecedor_selected', {}).get('id')

    if not fornecedor_id:
        return jsonify({'error': 'Fornecedor não selecionado'}), 400

    fornecedor = FornecedorController.get_fornecedor_por_id(fornecedor_id)
    if not fornecedor:
        return jsonify({'error': 'Fornecedor não encontrado'}), 400
    
    # Renderiza o template com os dados do fornecedor
    html_contrato = render_template('contrato_fornecedor.html', fornecedor=fornecedor.serialize())

    # Retorna o HTML para o frontend
    return html_contrato, 200


@assinatura_contrato_bp.route('/assina_contrato_fornecedor', methods=['POST'])
@login_required()
@role_required(['Fornecedor'])
def assina_contrato_fornecedor():
    usuario_logado = g.user_data
    
    if not usuario_logado or 'fornecedor_selected' not in usuario_logado:
        return jsonify({'error': 'Usuário ou fornecedor inválido.'}), 401
    
    session_id = request.cookies.get('session_id')
    assinatura, mensagem  = AssinaturaContratoFornecedor.get_or_create_assinatura_contrato_fornecedor(session_id, usuario_logado, g.tenant_url)

    if not assinatura:
        return jsonify({'msg':mensagem, 'data':{}}), 400

    # UsuarioController.get_usuario_por_username(usuario_logado)
    return jsonify({'msg':mensagem, 'data':{}}), 200

