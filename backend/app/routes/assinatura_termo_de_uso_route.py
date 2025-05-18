from flask import Blueprint,  jsonify, render_template, g, current_app, request # type: ignore
from app.controllers.assinatura_termo_de_uso_controller import AssinaturaTermoDeUsoController
from app.utils.decorators import login_required, role_required

assinatura_termo_bp = Blueprint('assinatura_termo', __name__) 


@assinatura_termo_bp.route('/get-termo', methods=['GET'])
@login_required()
def get_termos():
    html_termos = render_template('email_termos_de_uso.html')
    return html_termos, 200


@assinatura_termo_bp.route('/assina_termo', methods=['POST'])
@login_required()
@role_required(['Fornecedor', 'Parceiro'])
def assina_termo():
    usuario_logado = g.user_data

    if not usuario_logado:
        return jsonify({'error': 'Requisição inválida.'}), 401

    session_id = request.cookies.get('session_id')

    assinatura, mensagem = AssinaturaTermoDeUsoController.get_or_create_assinatura_termo_de_uso(session_id, usuario_logado, g.tenant_url)
    if not assinatura:
        return jsonify({'msg': mensagem, 'data': {}}), 400

    return jsonify({'msg': mensagem, 'data': {}}), 200