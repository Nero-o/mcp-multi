from app.repositories.assinatura_contrato_fornecedor_repository import AssinaturaContratoFornecedorRepository

class AssinaturaContratoFornecedorService:
    
    @staticmethod
    def get_assinatura_contrato_fornecedor(fornecedor_id, parceiro_id):        
        return AssinaturaContratoFornecedorRepository.get_assinatura_contrato_fornecedor(fornecedor_id, parceiro_id) 
    
    @staticmethod
    def registrar_assinatura_contrato_fornecedor(fornecedor_id, parceiro_id, dados_assinatura):
        return AssinaturaContratoFornecedorRepository.registrar_assinatura_contrato_fornecedor(fornecedor_id, parceiro_id, dados_assinatura)
