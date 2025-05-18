from app.repositories.fornecedor_nota_parcela_repository import FornecedorNotaParcelaRepository
from datetime import datetime

class FornecedorNotaParcelaService:
    
    # UPDATE
    @staticmethod
    def update_fornecedor_nota_parcela(parcela_id, dados):
        return FornecedorNotaParcelaRepository.update_fornecedor_nota_parcela(parcela_id, dados)
    
    # UPDATE específico para status admin
    @staticmethod
    def update_status_admin_parcela(parcela_id, status_id, user_id=None):
        """
        Atualiza o status administrativo da parcela e registra timestamp se necessário
        
        Args:
            parcela_id: ID da parcela a ser atualizada
            status_id: Novo status (1=Recebido, 4=Pago)
            user_id: ID do usuário que está fazendo a alteração (opcional)
        """
        dados = {
            'status_parcela_admin_id': status_id,
            'data_alteracao': datetime.now()
        }
        
        if user_id:
            dados['alterado_por'] = user_id
            
        return FornecedorNotaParcelaRepository.update_fornecedor_nota_parcela(parcela_id, dados) 