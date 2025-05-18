from flask import jsonify, current_app, render_template
from app.utils.hash import create_hash_assinatura
from app.utils.envia_email import envia_email
from app.services.redis_service import RedisService
from app.services.assinatura_termo_de_uso_service import AssinaturaTermoDeUsoService
from app.controllers.usuario_controller import UsuarioController
from app.controllers.parceiro_controller import ParceiroController

class AssinaturaTermoDeUsoController:

    @staticmethod
    def get_or_create_assinatura_termo_de_uso(session_id, usuario_logado, tenant_code):
        if not usuario_logado or 'username' not in usuario_logado or 'ip' not in usuario_logado or not tenant_code:
            return False, "Usuário ou tenant inválido."

        parceiro_da_url = ParceiroController.get_parceiro_por_tenant(tenant_code)
        if not parceiro_da_url:
            return False, "Requisição inválida."

        parceiro_id = parceiro_da_url.id
        fornecedor_id = None

        if 'Fornecedor' in usuario_logado['role']:
            if 'fornecedor_selected' not in usuario_logado:
                return False, "Usuário ou fornecedor inválido."
            
            fornecedor_id = usuario_logado['fornecedor_selected']['id']
            usuario = UsuarioController.get_usuario_por_fornecedor_parceiro(fornecedor_id, parceiro_id)
        else:
            usuario, mensagem = UsuarioController.valida_vinculo_usuario_parceiro_logado(usuario_logado, tenant_code)
            
        if not usuario:
            return False, mensagem
        
        usuario_id = usuario.id
        # Verificar se já existe uma assinatura para este usuário
        existe_assinatura = AssinaturaTermoDeUsoService.get_assinatura_termo_de_uso(parceiro_id, fornecedor_id, usuario_id)
        if existe_assinatura:
            return False, "Os termos de uso já foram assinados."

        nova_assinatura = AssinaturaTermoDeUsoController.create_assinatura_termo_de_uso(fornecedor_id, parceiro_id, usuario_id, usuario_logado['ip'])

        # Atualizar dados da sessão
        session_data = RedisService.get_session(session_id)
        if not session_data:
            return False, 'Dados da sessão não encontrados.'

        if 'Fornecedor' in usuario_logado['role']:
            session_data['user']['fornecedor_selected'].update({
                'termo_assinado': 1
            })
        else:
            session_data['user'].update({
                'termo_assinado': 1
            })

        RedisService.save_session(
            session_id,
            session_data,
            current_app.config['EXPIRATION_TIME_COOKIE']
        )

        return nova_assinatura, "Termos de uso assinados com sucesso."

    @staticmethod
    def create_assinatura_termo_de_uso(fornecedor_id, parceiro_id, usuario_id, ip):
        dados_assinatura = create_hash_assinatura({
            'fornecedor_id': fornecedor_id,
            'parceiro_id': parceiro_id,
            'usuario_id': usuario_id,
            'ip': ip
        }, tipo='termo')

        nova_assinatura = AssinaturaTermoDeUsoService.registrar_assinatura_termo_de_uso(fornecedor_id, parceiro_id, usuario_id, dados_assinatura)

        if not nova_assinatura:
            return False, "Falha ao registrar a assinatura dos termos de uso."

        usuario = UsuarioController.get_usuario_por_fornecedor_parceiro(fornecedor_id, parceiro_id)

        # Atualizar o status de assinatura nos dados do usuário
        UsuarioController.update_usuario(
            usuario.id,
            {'assinatura_termo_de_uso': 1}
        )
        
        result, status_code = envia_email(
            destinatarios=[nova_assinatura.fornecedor.email],
            assunto=f"{nova_assinatura.parceiro.nome} - Aceite termos de uso",
            corpo=render_template('email_termos_de_uso.html')
        )
        if status_code not in [202,200,'202','200']:
            current_app.logger.error(f"Erro ao enviar email de aceite de termos de uso para o fornecedor. [backend/app/controllers/assinatura_termo_de_uso_controller]: {result}")

        return True, "Termos de uso assinados com sucesso."
        