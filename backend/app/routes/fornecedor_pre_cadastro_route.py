from flask import Blueprint, request, jsonify, current_app
from app.services.fornecedor_pre_cadastro_service import FornecedorPreCadastroService
from app.utils.request_utils import get_client_ip, get_user_agent
import logging

bp = Blueprint('fornecedor_pre_cadastro', __name__)
service = FornecedorPreCadastroService()

@bp.route('/pre_cadastro_fornecedor', methods=['POST'])
def create_pre_cadastro():
    try:
        current_app.logger.info("Recebendo requisição de pré-cadastro")
        data = request.get_json()
        
        # Log dos dados recebidos (sem informações sensíveis)
        current_app.logger.info(f"Dados recebidos: {data.get('razao_social')}, {data.get('cpf_cnpj')}")
        
        data['ip_cadastro'] = get_client_ip(request)
        data['user_agent'] = get_user_agent(request)
        
        current_app.logger.info(f"IP do cliente: {data['ip_cadastro']}")
        current_app.logger.info(f"User Agent: {data['user_agent']}")
        
        result = service.create_pre_cadastro(data)
        current_app.logger.info("Pré-cadastro realizado com sucesso")
        
        return jsonify({
            'success': True,
            'message': 'Pré-cadastro realizado com sucesso',
            'data': result
        }), 201
        
    except ValueError as e:
        current_app.logger.error(f"Erro de validação: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        current_app.logger.error(f"Erro inesperado: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao processar pré-cadastro'
        }), 500