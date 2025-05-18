from flask import Blueprint, request, jsonify, g, current_app
from app.controllers.fornecedor_nota_parcela_controller import FornecedorNotaParcelaController
from app.utils.decorators import login_required, role_required
from app.services.fornecedor_nota_parcela_service import FornecedorNotaParcelaService

fornecedor_nota_parcela_bp = Blueprint('fornecedor_nota_parcela', __name__)

@fornecedor_nota_parcela_bp.route('/update_status_admin_parcela', methods=['POST'])
@login_required()
@role_required(['Administrador'])
def update_status_admin_parcela():
    """
    Atualiza o status administrativo de uma parcela
    """
    parcela_id = request.args.get('parcela_id', type=int)
    if not parcela_id:
        return jsonify({'msg': 'ID da parcela não fornecido.'}), 400
    
    payload = request.get_json()
    if not payload or 'status_admin' not in payload:
        return jsonify({'msg': 'Status ID não fornecido no corpo da requisição.'}), 400
    
    try:
        sucesso, mensagem = FornecedorNotaParcelaController.update_status_admin_parcela(
            parcela_id, 
            payload['status_admin']
        )
        
        if sucesso:
            parcela = FornecedorNotaParcelaService.update_fornecedor_nota_parcela(parcela_id, {})
            
            resposta = {
                'msg': mensagem,
                'parcela': {
                    'id': parcela.id,
                    'status_parcela_admin_id': parcela.status_parcela_admin_id,
                    'data_pagamento': parcela.data_pagamento.strftime('%Y-%m-%d') if parcela.data_pagamento else None
                }
            }
            
            return jsonify(resposta), 200
        else:
            current_app.logger.error(f"Erro ao atualizar status administrativo da parcela: {mensagem}")
            return jsonify({'msg': mensagem}), 400
            
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar status administrativo da parcela: {str(e)}")
        return jsonify({'msg': f'Erro ao atualizar status administrativo da parcela: {str(e)}'}), 500 
    


@fornecedor_nota_parcela_bp.route('/update_status_parcela', methods=['POST'])
@login_required()
@role_required(['Administrador'])
def update_status_parcela():
    """
    Atualiza o status administrativo de uma parcela
    """
    parcela_id = request.args.get('parcela_id', type=int)
    if not parcela_id:
        return jsonify({'msg': 'ID da parcela não fornecido.'}), 400
    
    payload = request.get_json()
    if not payload or 'status' not in payload:
        return jsonify({'msg': 'Status ID não fornecido no corpo da requisição.'}), 400
    
    try:
        sucesso, mensagem = FornecedorNotaParcelaController.update_status_parcela(
            parcela_id, 
            payload['status'],
            g.user_data,
            g.tenant_url
        )
        
        if sucesso:
            parcela = FornecedorNotaParcelaService.update_fornecedor_nota_parcela(parcela_id, {})
            
            resposta = {
                'msg': mensagem,
                'parcela': {
                    'id': parcela.id,
                    'status_parcela__id': parcela.status_parcela_id,
                }
            }
            
            return jsonify(resposta), 200
        else:
            current_app.logger.error(f"Erro ao atualizar status administrativo da parcela: {mensagem}")
            return jsonify({'msg': mensagem}), 400
            
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar status administrativo da parcela: {str(e)}")
        return jsonify({'msg': f'Erro ao atualizar status administrativo da parcela: {str(e)}'}), 500 