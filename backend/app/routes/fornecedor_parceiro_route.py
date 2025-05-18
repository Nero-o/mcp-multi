from flask import Blueprint, request, g, jsonify
from app.utils.decorators import login_required, role_required
from app.controllers.fornecedor_parceiro_controller import FornecedorParceiroController

fornecedor_parceiro_bp = Blueprint('fornecedor_parceiro_bp', __name__)


@fornecedor_parceiro_bp.route('/ativa_desativa_fornecedor', methods=['POST'])
@login_required()
@role_required(['Administrador', 'Parceiro', 'ParceiroAdministrador'])
def ativa_desativa_fornecedor():

    usuario_logado = g.user_data
    tenant_url = g.tenant_url
    fornecedor_id = request.args.get('fornecedor_id', type=int)

    data = request.get_json()
    habilitado = data.get('habilitado')

    fornecedor, mensagem = FornecedorParceiroController.ativa_desativa_fornecedor_parceiro(usuario_logado, tenant_url, fornecedor_id, habilitado)

    if fornecedor:
        return jsonify({'msg': mensagem}), 200
    else:
        return jsonify({'msg': mensagem}), 400


@fornecedor_parceiro_bp.route('/update_taxa_desconto_lote_fornecedor', methods=['POST'])
@login_required()
@role_required(['Administrador', 'Parceiro', 'ParceiroAdministrador'])
def update_taxa_desconto_lote_fornecedor():

    dados = request.get_json()
    usuario_logado = g.user_data
    tenant_url = g.tenant_url
      
    response, mensagem = FornecedorParceiroController.set_taxa_lote_fornecedor(usuario_logado, tenant_url, dados, 'taxa_desconto_lote')
    if response:
        return jsonify({'msg': mensagem}), 200
    else:
        return jsonify({'msg': mensagem}), 400


@fornecedor_parceiro_bp.route('/update_taxa_tac_lote_fornecedor', methods=['POST'])
@login_required()
@role_required(['Administrador', 'Parceiro', 'ParceiroAdministrador'])
def update_taxa_tac_lote_fornecedor():
    
    dados = request.get_json()
    usuario_logado = g.user_data
    tenant_url = g.tenant_url

    response, mensagem = FornecedorParceiroController.set_taxa_lote_fornecedor(usuario_logado, tenant_url, dados, 'taxa_tac_lote')
    if response:
        return jsonify({'msg': mensagem}), 200
    else:
        return jsonify({'msg': mensagem}), 400


@fornecedor_parceiro_bp.route('/update_taxa_desconto_individual_fornecedor', methods=['POST'])
@login_required()
@role_required(['Administrador', 'Parceiro', 'ParceiroAdministrador'])
def update_taxa_desconto_individual_fornecedor():

    dados = request.get_json()
    usuario_logado = g.user_data
    tenant_url = g.tenant_url

    response, mensagem = FornecedorParceiroController.set_taxa_individual_fornecedor(usuario_logado,tenant_url, dados, 'taxa_desconto_individual')

    if response:
        return jsonify({'msg': mensagem}), 200
    else:
        return jsonify({'msg': mensagem}), 400


@fornecedor_parceiro_bp.route('/update_taxa_tac_individual_fornecedor', methods=['POST'])
@login_required()
@role_required(['Administrador', 'Parceiro', 'ParceiroAdministrador'])
def update_taxa_individual_fornecedor():
    
    dados = request.get_json()
    usuario_logado = g.user_data
    tenant_url = g.tenant_url

    response, mensagem = FornecedorParceiroController.set_taxa_individual_fornecedor(usuario_logado, tenant_url, dados, 'taxa_tac_individual')
    if response:
        return jsonify({'msg': mensagem}), 200
    else:
        return jsonify({'msg': mensagem}), 400
