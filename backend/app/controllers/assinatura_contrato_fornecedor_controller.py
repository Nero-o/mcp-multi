import hashlib
from datetime import datetime
from flask import request, jsonify, current_app, render_template
from app.utils.hash import create_hash_assinatura
from app.utils.envia_email import envia_email
from app.controllers.usuario_controller import UsuarioController
from app.services.parceiro_service import ParceiroService
from app.services.redis_service import RedisService
from app.services.fornecedor_service import FornecedorService
from app.services.assinatura_contrato_fornecedor_service import AssinaturaContratoFornecedorService
from flask import current_app

class AssinaturaContratoFornecedor:
    
    @staticmethod
    def get_or_create_assinatura_contrato_fornecedor(session_id, usuario_logado, tenant_code):
        if not usuario_logado or 'fornecedor_selected' not in usuario_logado or 'username' not in usuario_logado or 'ip' not in usuario_logado or not tenant_code:
            return False, "Usuário ou tenant inválido. 1"

        parceiro_da_url = ParceiroService.get_parceiro_por_tenant(tenant_code)
        if not parceiro_da_url:
            return False, "Requisição inválida. 1"
        
        usuario = UsuarioController.get_usuario_por_fornecedor_parceiro(usuario_logado['fornecedor_selected']['id'], parceiro_da_url.id)
        if not usuario:
            return False, "Requisição inválida. 2"
 
        parceiro_id = parceiro_da_url.id
        fornecedor_id = usuario_logado['fornecedor_selected']['id']

        if not parceiro_id or not parceiro_id or parceiro_id != parceiro_da_url.id:
            return False, "Requisição inválida. 3"
        
        existe_assinatura = AssinaturaContratoFornecedorService.get_assinatura_contrato_fornecedor(fornecedor_id, parceiro_id)
        if existe_assinatura:
            return False, "Este contrato já foi assinado."

        usuario, mensagem = UsuarioController.valida_vinculo_usuario_parceiro_logado(usuario_logado, tenant_code)
        if not usuario:
            return False, mensagem
        
        nova_assinatura, mensagem = AssinaturaContratoFornecedor.create_assinatura_contrato_fornecedor(fornecedor_id, parceiro_id, usuario_logado['ip'])
        if not nova_assinatura:
            return False, mensagem
        
        session_data = RedisService.get_session(session_id)
        if not session_data:
            return jsonify({'error': 'Dados da sessão não encontrados.'}), 401
        
        session_data['user']['fornecedor_selected'].update({
            'contrato_assinado': 1
        })

        RedisService.save_session(
            session_id,
            session_data,
            current_app.config['EXPIRATION_TIME_COOKIE']
        ) 

        result, status_code = envia_email(
            destinatarios=[
                nova_assinatura.fornecedor.email
            ],
            assunto=f"{nova_assinatura.parceiro.nome} - Aceite contrato de securitização",
            corpo=render_template(
                'email_contrato_assinado.html',
                fornecedor=nova_assinatura.fornecedor,
                nova_assinatura=nova_assinatura
            )
        )
        if status_code not in [202, 200, '202', '200']:
            current_app.logger.error(f"Erro ao enviar email do contrato. [backend/app/controllers/assinatura_contrato_fornecedor_controller]: {result}")
            return False, "Erro ao enviar email do contrato."
        
        result, status_code = envia_email(
            destinatarios=[
                nova_assinatura.fornecedor.email
            ],
            assunto=f"{nova_assinatura.parceiro.nome} - Confirmação de aceite",
            corpo=render_template(
                'email_aceite_contratos.html',
                fornecedor=nova_assinatura.fornecedor,
                parceiro=parceiro_da_url,
            )
        )
        
        if status_code not in [202, 200, '202', '200']:
            current_app.logger.error(f"Erro ao enviar email de confirmação de aceite do contrato. [backend/app/controllers/assinatura_contrato_fornecedor_controller]: {result}")
            return False, "Erro ao enviar email de confirmação de aceite do contrato."
        
        return nova_assinatura, "Contrato assinado com sucesso."

        
    @staticmethod
    def create_assinatura_contrato_fornecedor(fornecedor_id, parceiro_id, ip):
        dados_assinatura = create_hash_assinatura({
            'fornecedor_id': fornecedor_id,
            'parceiro_id': parceiro_id,
            'ip': ip
        }, tipo='contrato')
        
        registra_assinatura = AssinaturaContratoFornecedorService.registrar_assinatura_contrato_fornecedor(
            fornecedor_id,
            parceiro_id,
            dados_assinatura
        ) 

        usuario = UsuarioController.get_usuario_por_fornecedor_parceiro(fornecedor_id, parceiro_id)

        if not usuario:
            return False, "Usuário não encontrado."
        
        UsuarioController.update_usuario(
            usuario.id,
            {'assinatura_contrato': 1}
        )
        if registra_assinatura:
            return registra_assinatura, "Contrato assinado com sucesso."
        else:
            return False, "Falha ao registrar a assinatura do contrato."

