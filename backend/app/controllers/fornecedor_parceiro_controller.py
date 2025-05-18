from flask import current_app, render_template
from app.services.fornecedor_parceiro_service import FornecedorParceiroService
from app.services.parceiro_service import ParceiroService
from app.services.fornecedor_service import FornecedorService
from app.services.usuario_service import UsuarioService
from app.controllers.usuario_controller import UsuarioController
from app.utils.envia_email import envia_email

class FornecedorParceiroController:

    @staticmethod
    def ativa_desativa_fornecedor_parceiro(usuario_logado, tenant_url, fornecedor_id, habilitado):

        parceiro_url = ParceiroService.get_parceiro_por_tenant(tenant_url)
        fornecedor = FornecedorService.get_fornecedor_por_id(fornecedor_id)
        fornecedor_parceiro = FornecedorParceiroService.get_fornecedor_parceiro(parceiro_url.id, fornecedor_id)
        usuario_fornecedor_parceiro = UsuarioService.get_usuario_por_fornecedor_parceiro(fornecedor.id, parceiro_url.id)

        CAMPOS_OBRIGATORIOS = [
            'cpf_cnpj',
            'socio_representante',
            'cpf_representante',
            'email',
            'bco',
            'agencia',
            'conta'
        ]

        if not fornecedor_parceiro:
            return False, "Fornecedor não encontrado. 01"

        if not fornecedor:
            return False, "Fornecedor não encontrado. 02"
        
        if usuario_logado['role'] in ['Parceiro', 'ParceiroAdministrador']:
            usuario = UsuarioController.get_usuario_por_username(usuario_logado['username'], parceiro_url.id)
            if not usuario:
                return False, "Usuário não encontrado."           
        
        aux_dict = {
            0: 'habilitado',
            1: 'desabilitado'
        }

        valor_atual = aux_dict[fornecedor_parceiro.excluido]
        novo_valor = aux_dict[habilitado]

        if valor_atual == novo_valor:
            return False, f"Fornecedor já está {valor_atual}." 
        
        if novo_valor == 'habilitado':
            campos_nao_preenchidos = []

            for campo in CAMPOS_OBRIGATORIOS:
                valor = getattr(fornecedor, campo, None)
                if valor is None or (isinstance(valor, str) and not valor.strip()):
                    campos_nao_preenchidos.append(campo)

            if len(campos_nao_preenchidos) > 0:
                for campo in campos_nao_preenchidos:
                    string_campos = ", ".join(campos_nao_preenchidos)

                return False, f"Os campos {string_campos.upper()} são obrigatórios para habilitar o acesso."

        FornecedorParceiroService.update_fornecedor_parceiro_individual(
            fornecedor_id=fornecedor_id,
            parceiro_id=parceiro_url.id,
            dados={
                'excluido': habilitado
            })
        
        if novo_valor == 'desabilitado':
            return fornecedor, f"Fornecedor {novo_valor} com sucesso."
        
        usuario_fornecedor = UsuarioController.get_usuario_por_fornecedor_parceiro(fornecedor_id, parceiro_url.id)
        idpUserId = usuario_fornecedor.idpUserId

        if usuario_fornecedor.email_primeiro_acesso == 1 and usuario_fornecedor.senha_temporaria != "":
            primeiro_acesso = 0
        else:
            primeiro_acesso = 1
        
        result, status_code = envia_email(
            destinatarios=[fornecedor.email],
            assunto=f"{parceiro_url.nome} - Portal Risco Sacado - Seu acesso ao portal foi liberado.",
            corpo=render_template(
                'email_acesso_liberado_fornecedor.html',
                fornecedor=fornecedor,
                parceiro=parceiro_url,
                login=fornecedor.email,
                primeiro_acesso=primeiro_acesso,
                senha=usuario_fornecedor_parceiro.senha_temporaria
            )
        )
        if status_code not in [202,200,'202','200']:
            current_app.logger.error(f"Erro ao enviar email de acesso liberado para o fornecedor. [backend/app/controllers/fornecedor_parceiro_controller]: {result}")
        

        updated = UsuarioController.update_usuario_por_idp_user_id(idpUserId, {'email_primeiro_acesso': 1})
        current_app.logger.info(f"Usuário atualizado ao habilitar: {updated}")
        return fornecedor, f"Fornecedor {novo_valor} com sucesso."

    @staticmethod
    def set_taxa_lote_fornecedor(usuario_logado, tenant_url, dados, campo_taxa):
            
        if dados.get(campo_taxa) != 0 and not dados.get(campo_taxa):
            return False, "Requisição inválida. STLF04"
        
        ## sobrescreve "dados" pra nao ter valores inesperados
        dados = {
            campo_taxa: dados.get(campo_taxa)
        }

        role = usuario_logado['role'][0]

        usuario_parceiro, mensagem = UsuarioController.valida_vinculo_usuario_parceiro_logado(usuario_logado, tenant_url)

        if not usuario_parceiro:
            return False, "Requisição inválida. STLF04"
        
        if role == 'Administrador':
            parceiro_id = usuario_parceiro.parceiro_id
        
        elif role == 'Parceiro' or role == 'ParceiroAdministrador':
            parceiro = ParceiroService.get_parceiro_por_id(usuario_parceiro.parceiro_id)
            if parceiro.tenant_code != tenant_url:
                return False, "Requisição inválida. STLF05"
            parceiro_id = parceiro.id
        
        if not parceiro_id:
            return False, "Requisição inválida. STLF06"
        
        FornecedorParceiroService.update_fornecedor_parceiro_lote(parceiro_id, dados) 
            
        return True, "Taxa de desconto atualizada para todos os fornecedores com sucesso." 


    @staticmethod
    def set_taxa_individual_fornecedor(usuario_logado, tenant_url, dados, campo_taxa):

        fornecedor_id = dados['fornecedor_id']
        
        if dados.get(campo_taxa) != 0 and not dados.get(campo_taxa):
            return False, "Requisição inválida. STIF01"
        
        ## sobrescreve "dados" pra nao ter valores inesperados, 
        # deixando somente o campo que a rota está solicitando para alteração
        dados = {
            campo_taxa: dados.get(campo_taxa)
        }
        
        role = usuario_logado['role'][0]
        
        if role == 'Administrador':
            parceiro = ParceiroService.get_parceiro_por_tenant(tenant_url)

        if role == 'Parceiro' or role == 'ParceiroAdministrador':
            usuario_parceiro, mensagem = UsuarioController.valida_vinculo_usuario_parceiro_logado(usuario_logado, tenant_url)
            if not usuario_parceiro:
                return False, "Requisição inválida. STIF02"
            parceiro = ParceiroService.get_parceiro_por_id(usuario_parceiro.parceiro_id)

        if not parceiro:
            return False, "Requisição inválida. STDIF03"
        
        parceiro_id = parceiro.id

        fornecedor_parceiro_atualizado = FornecedorParceiroService.update_fornecedor_parceiro_individual(fornecedor_id, parceiro_id, dados)
        if fornecedor_parceiro_atualizado:
            return True, 'Taxa do fornecedor atualizada com sucesso.' 
        else:
            return False, 'Nenhuma taxa foi atualizada'