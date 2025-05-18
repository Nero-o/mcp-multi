from datetime import datetime
from flask import g, current_app
from app.services.fornecedor_nota_parcela_service import FornecedorNotaParcelaService
from app.controllers.usuario_controller import UsuarioController
from app.services.parceiro_service import ParceiroService

class FornecedorNotaParcelaController:
    
    @staticmethod
    def update_status_parcela(parcela_id, status_id, usuario_logado, tenant_code_url):
        # Verifica vínculo do usuário com o parceiro
        usuario_valido, mensagem = UsuarioController.valida_vinculo_usuario_parceiro_logado(
            usuario_logado,
            tenant_code_url
        )
        if not usuario_valido:
            return False, mensagem
        
        # Atualiza o status da parcela
        try:
            parcela = FornecedorNotaParcelaService.update_fornecedor_nota_parcela(
                parcela_id,
                {'status_parcela_id': status_id, 'data_alteracao': datetime.now()}
            )
            
            if parcela:
                return True, f"Status da parcela atualizado com sucesso"
            else:
                return False, "Parcela não encontrada ou não foi possível atualizá-la"
        except Exception as e:
            current_app.logger.error(f"Erro ao atualizar status da parcela: {str(e)}")
            return False, f"Erro ao atualizar status da parcela: {str(e)}"
    
    @staticmethod
    def update_status_admin_parcela(parcela_id, status_id):
        try:
            # Obter o ID do usuário logado se disponível
            user_id = getattr(g, 'user_id', None)
            
            # Usar o serviço específico para atualização de status
            parcela = FornecedorNotaParcelaService.update_status_admin_parcela(
                parcela_id, 
                status_id,
                user_id
            )
            
            if parcela:
                # Verificar se é um status que requer registro de data_pagamento
                if status_id in [1, 4]:  # Recebido ou Pago
                    data_formatada = parcela.data_pagamento.strftime('%d/%m/%Y') if parcela.data_pagamento else 'N/A'
                    mensagem = f"Status admin da parcela atualizado para {'Recebido' if status_id == 1 else 'Pago'} com data de pagamento: {data_formatada}"
                else:
                    mensagem = "Status admin da parcela atualizado com sucesso"
                return True, mensagem
            else:
                return False, "Parcela não encontrada ou não foi possível atualizá-la"
        except Exception as e:
            current_app.logger.error(f"Erro ao atualizar status admin da parcela: {str(e)}")
            return False, f"Erro ao atualizar status admin da parcela: {str(e)}" 