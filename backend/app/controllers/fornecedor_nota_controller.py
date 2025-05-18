# app/controllers/fornecedor_nota_controller.py
from datetime import datetime
from flask import g, current_app, render_template
from sqlalchemy import and_
from app.services.fornecedor_nota_service import FornecedorNotaService
from app.controllers.usuario_controller import UsuarioController
from app.services.parceiro_service import ParceiroService
from app.models.fornecedor_nota_model import FornecedorNota
from app.models.fornecedor_model import Fornecedor
from app.utils.paginacao import PaginacaoHelper
from app.utils.serializer import Serializer
from app.utils.envia_email import envia_email
from app.utils.formata_monetario import formata_monetario
from app.utils.helpers import force_str_to_date_obj

class FornecedorNotaController:
    @staticmethod
    def contas_a_pagar(usuario_logado, tenant_code_url, page, per_page):
        # Verifica vínculo do usuário com o parceiro
        usuarios_validos, mensagem = UsuarioController.valida_vinculo_usuario_parceiro_logado(
            usuario_logado,
            tenant_code_url,
            retorna_lista_usuarios=True
        )
        if not usuarios_validos:
            return None, mensagem

        parceiro_da_url = ParceiroService.get_parceiro_por_tenant(tenant_code_url)
        
        # Define filtro base
        filtro_base = FornecedorNota.tipo_operacao == 'parceiro_sacado'
        
        # Se for parceiro, adiciona filtro adicional
        if usuario_logado['role'][0] in ['Parceiro', 'ParceiroAdministrador']:
            usuario_parceiro = usuarios_validos[0]
            filtro_base = and_(
                filtro_base,
                FornecedorNota.parceiro_id == usuario_parceiro.parceiro_id
            )
        elif usuario_logado['role'][0] == 'Administrador':
            filtro_base = and_(
                filtro_base,
                FornecedorNota.parceiro_id == parceiro_da_url.id
            )

        notas = FornecedorNotaService.get_all_fornecedor_nota_join(
            join_model=Fornecedor,
            add_columns=[Fornecedor.razao_social, Fornecedor.cpf_cnpj],
            filter=filtro_base
        ).all()

        if not notas:
            return None, "Nenhuma nota encontrada."

        # Lista para armazenar todas as parcelas
        todas_parcelas = []
        valor_total = 0
        valor_pago = 0
        valor_pendente  = 0
        
        # Para cada nota, busca suas parcelas
        for nota in notas:
            parcelas = FornecedorNotaService.get_parcelas(nota[0].id)  # nota[0] porque o join retorna uma tupla
            for parcela in parcelas:
                valor_parcela = parcela.valor or 0

                if parcela.status_parcela_admin_id == 1:  # Recebido
                    valor_recebido += valor_parcela
                    current_app.logger.info(f"Valor recebido: {valor_recebido}")
                
                if parcela.status_parcela_admin_id == 2:
                    valor_total += valor_parcela
                    current_app.logger.info(f"Valor total: {valor_total}")

                elif parcela.status_parcela_admin_id == 3:  # Em atraso
                    valor_em_atraso += valor_parcela
                    current_app.logger.info(f"Valor em atraso: {valor_em_atraso}")
                    
                data_vencimento = force_str_to_date_obj(parcela.data_vencimento)

                todas_parcelas.append({
                    "id": parcela.id,
                    "operacao_id": parcela.operacao_id,
                    "valor": parcela.valor,
                    "data_vencimento": data_vencimento.strftime("%d/%m/%Y") if data_vencimento else None,
                    "status": parcela.status_parcela.id if parcela.status_parcela else 1,
                    "status_admin": parcela.status_parcela_admin.id if parcela.status_parcela_admin else 1,
                    "fornecedor": {
                        "razao_social": nota.razao_social,
                        "cpf_cnpj": nota.cpf_cnpj
                    }
                })

        # Implementar paginação manual das parcelas
        total_parcelas = len(todas_parcelas)
        inicio = (page - 1) * per_page
        fim = inicio + per_page
        parcelas_paginadas = todas_parcelas[inicio:fim]

        return {
            "header":{
                "valor_total": formata_monetario(valor_total, '.', ','),
                "valor_pago": formata_monetario(valor_pago, '.', ','),
                "valor_pendente": formata_monetario(valor_pendente, '.', ',')
            },
            "items": parcelas_paginadas,
            "total": total_parcelas,
            "page": page,
            "per_page": per_page,
            "pages": (total_parcelas + per_page - 1) // per_page
        }, "Sucesso"


    @staticmethod
    def contas_a_receber(usuario_logado, tenant_code_url, page, per_page):
        # Verifica vínculo do usuário com o parceiro
        parceiro_da_url = ParceiroService.get_parceiro_por_tenant(tenant_code_url)
        
        filtros = [
            FornecedorNota.parceiro_id == parceiro_da_url.id,
            FornecedorNota.excluido == 0
        ]

        # Adiciona filtro de tipo_operacao apenas para usuários tipo parceiro
        if usuario_logado['role'][0] in ['Parceiro', 'ParceiroAdministrador']:
            filtros.append(FornecedorNota.tipo_operacao == 'parceiro_cedente')
        
        # Adiciona filtro específico para fornecedor quando aplicável
        if usuario_logado['role'][0] == 'Fornecedor':
            filtros.append(FornecedorNota.fornecedor_id == usuario_logado['fornecedor_selected']['id'])
        
        # Combina todos os filtros
        filtro_query = and_(*filtros)

        # Busca as notas com join em Fornecedor
        notas = FornecedorNotaService.get_all_fornecedor_nota_join(
            join_model=Fornecedor,
            join_on=FornecedorNota.fornecedor_id == Fornecedor.id,
            add_columns=[Fornecedor.razao_social, Fornecedor.cpf_cnpj],
            filter=filtro_query
        ).all()

        if not notas:
            return None, "Nenhuma nota encontrada."

        # Lista para armazenar todas as parcelas
        todas_parcelas = []
        valor_total = 0
        valor_recebido = 0
        valor_em_atraso = 0

        # Para cada nota, busca suas parcelas
        for nota in notas:
            parcelas = FornecedorNotaService.get_parcelas(nota[0].id)  # nota[0] porque o join retorna (Nota, Razao Social, CPF/CNPJ)
            
            for parcela in parcelas:
                current_app.logger.info(f" Parcela: {parcela.id}")
                
                valor_parcela = parcela.valor if parcela.valor else 0
                
                if parcela.status_parcela_admin_id == 1:  # Recebido
                    valor_recebido += valor_parcela
                
                if parcela.status_parcela_admin_id == 2:
                    valor_total += valor_parcela

                elif parcela.status_parcela_admin_id == 3:  # Em atraso
                    valor_em_atraso += valor_parcela

                data_vencimento = force_str_to_date_obj(parcela.data_vencimento)

                todas_parcelas.append({
                    "id": parcela.id,
                    "operacao_id": parcela.operacao_id,
                    "valor": parcela.valor,
                    "data_vencimento": data_vencimento.strftime("%d/%m/%Y") if data_vencimento else None,
                    "status": parcela.status_parcela.id if parcela.status_parcela else 1,
                    "status_admin": parcela.status_parcela_admin.id if parcela.status_parcela_admin else 1,
                    "fornecedor": {
                        "razao_social": nota.razao_social,
                        "cpf_cnpj": nota.cpf_cnpj
                    }
                })

        # Implementar paginação manual das parcelas
        total_parcelas = len(todas_parcelas)
        inicio = (page - 1) * per_page
        fim = inicio + per_page
        parcelas_paginadas = todas_parcelas[inicio:fim]

        return {
            "header":{
                "valor_total": formata_monetario(valor_total, '.', ','),
                "valor_recebido": formata_monetario(valor_recebido, '.', ','),
                "valor_em_atraso": formata_monetario(valor_em_atraso, '.', ',')
            },
            "items": parcelas_paginadas,
            "total": total_parcelas,
            "page": page,
            "per_page": per_page,
            "pages": (total_parcelas + per_page - 1) // per_page
        }, "Sucesso"

    @staticmethod
    def get_parcelas(nota_id):
        parcelas = FornecedorNotaService.get_parcelas(nota_id)
        
        # Transformando os dados para o formato esperado pelo frontend
        items = []
        for parcela in parcelas:
            data_vencimento = force_str_to_date_obj(parcela.data_vencimento)
            items.append({
                "id": parcela.id,
                "documento": parcela.operacao.documento,  # Ou outro campo que represente o documento
                "valor": parcela.valor,
                "data_vencimento": data_vencimento.strftime("%Y-%m-%d") if data_vencimento else None,
                "status": parcela.status_parcela_admin.id if parcela.status_parcela_admin else 0
            })
        
        # Retornando no formato esperado pelo frontend
        return {"items": items}
    
    @staticmethod
    def ativa_desativa_nota(nota_id, habilitado):
        nota = FornecedorNotaService.get_fornecedor_nota_por_id(nota_id)
        if not nota:
            return False, "Nota não encontrada."
        
        aux_dict = {
            0: 'habilitada',
            1: 'desabilitada'
        }

        nota_excluida = aux_dict[nota.excluido]
        nota_nova_excluida = aux_dict[habilitado]

        if nota_excluida == nota_nova_excluida:
            return False, f"Nota já está {nota_nova_excluida} para o usuário."

        FornecedorNotaService.update_fornecedor_nota(
            nota_id,
            {'excluido': habilitado}
        )
        return True, f"Nota {nota_nova_excluida} com sucesso."

    @staticmethod
    def update_status_admin_nota(nota_id, status_id):
        FornecedorNotaService.update_fornecedor_nota(
            nota_id,
            {'status_admin_id': status_id}
        )
        return True, "Status atualizado com sucesso."

    @staticmethod
    def conclui_nota(nota_id):
        
        nota = FornecedorNotaService.get_fornecedor_nota_por_id(nota_id)
        if not nota:
            return False, "Nota não encontrada."
        
        if nota.status_id == 3:
            return False, "Nota EXPIRADA não pode ser concluída." 
        if nota.status_id == 4:
            return False, "Nota CONCLUÍDA não pode ser concluída."
        if nota.status_id == 5:
            return False, "Nota CANCELADA não pode ser concluída."
        
        # Validar usuário e parceiro
        to_update = {
            'status_id': 4,
            'data_conclusao': datetime.now()
        }

        FornecedorNotaService.update_fornecedor_nota(
            nota_id,
            to_update
        )
        result, status_code = envia_email(
            destinatarios=[nota.fornecedor.email],
            assunto=f"{nota.parceiro.nome} - Nota concluída.",
            corpo=render_template(
                'email_nota_concluida.html',
                nota=nota,
                parceiro=nota.parceiro
            )
        )
        if status_code not in [202,200,'202','200']:
            current_app.logger.error(f"Erro ao enviar email NOTA CONCLUÍDA para o fornecedor. [backend/app/controllers/fornecedor_nota_controller]: {result}")
        
        return True, "Nota concluída com sucesso."
    
    @staticmethod
    def cancela_nota(nota_id):
        nota = FornecedorNotaService.get_fornecedor_nota_por_id(nota_id)
        if not nota:
            return False, "Nota não encontrada."
        
        if nota.status_id == 3:
            return False, "Nota EXPIRADA não pode ser cancelada." 
        if nota.status_id == 5:
            return False, "Nota CANCELADA não pode ser cancelada."

        to_update = {
            'status_id': 5,
            'data_cancelamento': datetime.now()
        }
        # Validar usuário e parceiro
        FornecedorNotaService.update_fornecedor_nota(
            nota_id,
            to_update
        )

        result, status_code = envia_email(
            destinatarios=[nota.fornecedor.email],
            assunto=f"{nota.parceiro.nome} - Nota cancelada.",
            corpo=render_template(
                'email_nota_cancelada.html',
                nota=nota,
                parceiro=nota.parceiro
            )
        )
        if status_code not in [202,200,'202','200']:
            current_app.logger.error(f"Erro ao enviar email NOTA CANCELADA para o fornecedor. [backend/app/controllers/fornecedor_nota_controller]: {result}")
            return True, "Erro ao enviar email NOTA CANCELADA para o fornecedor."
        
        return True, "Nota cancelada com sucesso."
    

    @staticmethod
    def get_all_fornecedor_nota_paginacao(lista_status, page, per_page, usuario_logado):
        # Verifica se o usuário está vinculado ao parceiro (tenant) solicitado
        usuarios_validos, mensagem = UsuarioController.valida_vinculo_usuario_parceiro_logado(
            usuario_logado,
            g.tenant_url,
            retorna_lista_usuarios=True
        )
        if not usuarios_validos:
            return [], mensagem

        parceiro_da_url = ParceiroService.get_parceiro_por_tenant(g.tenant_url)
        filtro_status = FornecedorNota.status_id.in_(lista_status)

        if isinstance(usuario_logado['role'], list):
            role = usuario_logado['role'][0]
        else:
            role = usuario_logado['role']


        if role == 'Fornecedor':
            notas_query = FornecedorNotaController.aux_get_all_fornecedor(usuario_logado, usuarios_validos, parceiro_da_url, filtro_status)
            
        elif role == 'Administrador':
            notas_query = FornecedorNotaController.aux_get_all_administrador(parceiro_da_url, filtro_status)
        
        elif role in ['Parceiro', 'ParceiroAdministrador']:
            notas_query = FornecedorNotaController.aux_get_all_parceiro(usuarios_validos, filtro_status)
        else:
            return None
        
        if not notas_query:
            return None
        
        # Aplicar paginação
        # Retornar as notas e a mensagem de sucesso
        return PaginacaoHelper.paginate_query(
            notas_query,
            page,
            per_page,
            serialize_func=Serializer.serialize_nota
        )

    @staticmethod
    def aux_get_all_parceiro(usuarios_validos, filtro_status):
        # Obter o usuário parceiro
        usuario_parceiro = usuarios_validos[0]
        current_app.logger.error(f"Usuario parceiro: {usuario_parceiro}")
        parceiro_id = usuario_parceiro.parceiro_id
        
        # Definir a expressão de filtro
        filtro_parceiro = and_(
            FornecedorNota.parceiro_id == parceiro_id,
            filtro_status
        )
        
        # Chamar o método adaptado
        notas_query = FornecedorNotaService.get_all_fornecedor_nota_join(
            join_model=Fornecedor,
            add_columns=[Fornecedor.razao_social, Fornecedor.cpf_cnpj],
            filter=filtro_parceiro
        )

        return notas_query
    
    @staticmethod
    def aux_get_all_fornecedor(usuario_logado, usuarios_validos, parceiro_da_url, filtro_status):
        #Coleta somente o id do fornecedor selecionado pelo usuário (sessao/cookie)
        fornecedor_ids = {usuario_logado['fornecedor_selected']['id']}
        filtro_query = and_(
            FornecedorNota.fornecedor_id.in_(fornecedor_ids),
            FornecedorNota.parceiro_id == parceiro_da_url.id,
            filtro_status
        )

        # Busca campos do fornecedor
        notas_query = FornecedorNotaService.get_all_fornecedor_nota_join(
            join_model=Fornecedor,
            add_columns=[Fornecedor.razao_social, Fornecedor.cpf_cnpj],
            filter=filtro_query
        )
        return notas_query
    
    @staticmethod
    def aux_get_all_administrador(parceiro_da_url, filtro_status):
        filtro_query = and_(
            FornecedorNota.parceiro_id == parceiro_da_url.id,
            filtro_status
        )
        
        # Chamar o método adaptado
        notas_query = FornecedorNotaService.get_all_fornecedor_nota_join(
            join_model=Fornecedor,
            add_columns=[Fornecedor.razao_social, Fornecedor.cpf_cnpj],
            filter=filtro_query
        )
        return notas_query
    



    @staticmethod
    def detalhe_fornecedor_nota(fornecedor_nota_id, usuario_logado, tenant_code_url):
        role_usuario = usuario_logado['role'][0]
        parceiro_da_url = ParceiroService.get_parceiro_por_tenant(tenant_code_url)
        
        if role_usuario == 'Administrador': 
            fornecedor_nota = FornecedorNotaService.get_fornecedor_nota_por_id_join_fornecedor(
                fornecedor_nota_id=fornecedor_nota_id
            ).first()

        elif role_usuario == 'Parceiro' or role_usuario == 'ParceiroAdministrador':            
            usuario_parceiro, mensagem = UsuarioController.valida_vinculo_usuario_parceiro_logado(usuario_logado, tenant_code_url)
            if not usuario_parceiro:
                return False, mensagem
            parceiro_id = usuario_parceiro.parceiro_id
            fornecedor_nota = FornecedorNotaService.get_fornecedor_nota_por_id_join_fornecedor(
                fornecedor_nota_id=fornecedor_nota_id,
                parceiro_id=parceiro_id
            ).first()

        elif role_usuario == 'Fornecedor':
            if not 'fornecedor_selected' in usuario_logado or not usuario_logado['fornecedor_selected']:
                return False, f"Usuário não possui fornecedor selecionado."
            
            parceiro_id = parceiro_da_url.id
            fornecedor_id = usuario_logado['fornecedor_selected']['id']

            fornecedor_nota = FornecedorNotaService.get_fornecedor_nota_por_id_join_fornecedor(
                fornecedor_nota_id=fornecedor_nota_id,
                parceiro_id=parceiro_id,
                fornecedor_id=fornecedor_id
            ).first() 
        else:
            return False, "Acesso negado. DNT01"

        
        if not fornecedor_nota:
            return False, f"Nota não encontrada."
        
        fornecedor_nota_serialized = Serializer.serialize_nota(fornecedor_nota)

        return fornecedor_nota_serialized, f"Sucesso."

    
    # READ
    @staticmethod
    def get_all_fornecedor_nota(limit=None, offset=None):
        return FornecedorNotaService.get_all_fornecedor_nota(limit, offset)

    # CREATE
    @staticmethod
    def create_fornecedor_nota(dados):
        return FornecedorNotaService.create_fornecedor_nota(dados)

    # UPDATE
    @staticmethod
    def update_fornecedor_nota(fornecedor_nota_id, dados):
        return FornecedorNotaService.update_fornecedor_nota(fornecedor_nota_id, dados)

    # DELETE
    @staticmethod
    def delete_fornecedor_nota(fornecedor_nota_id):
        return FornecedorNotaService.delete_fornecedor_nota(fornecedor_nota_id)

    @staticmethod
    def get_fornecedor_nota_por_id(fornecedor_nota_id):
        return FornecedorNotaService.get_fornecedor_nota_por_id(fornecedor_nota_id)
    
    @staticmethod
    def get_fornecedor_nota_por_id_join_fornecedor(fornecedor_nota_id):
        return FornecedorNotaService.get_fornecedor_nota_por_id_join_fornecedor(fornecedor_nota_id)
