from app.repositories.fornecedor_parceiro_repository import FornecedorParceiroRepository

class FornecedorParceiroService:
    @staticmethod
    def get_fornecedor_parceiro(parceiro_id, fornecedor_id):
        return FornecedorParceiroRepository.get_fornecedor_parceiro(parceiro_id, fornecedor_id)
    
    @staticmethod
    def get_fornecedor_parceiro_por_parceiro_id(parceiro_id, excluido=None):
        return FornecedorParceiroRepository.get_fornecedor_parceiro_por_parceiro_id(parceiro_id, excluido)
    
    # UPDATE LOTE
    @staticmethod
    def update_fornecedor_parceiro_lote(parceiro_id, dados):
        return FornecedorParceiroRepository.update_fornecedor_parceiro_lote(parceiro_id, dados)
    
    # UPDATE INDIVIDUAL
    @staticmethod
    def update_fornecedor_parceiro_individual(fornecedor_id, parceiro_id, dados):
        return FornecedorParceiroRepository.update_fornecedor_parceiro_individual(fornecedor_id, parceiro_id, dados)