from app.repositories.assinatura_fornecedor_nota_repository import AssinaturaFornecedorNotaRepository

class AssinaturaFornecedorNotaService:
    
    @staticmethod
    def get_assinatura_por_nota_e_usuario(nota_id, usuario_id):
        return AssinaturaFornecedorNotaRepository.get_assinatura_por_nota_e_usuario(nota_id, usuario_id)
    
    @staticmethod
    def registrar_assinatura_nota(usuario_id, nota_id, dados_assinatura):
        return AssinaturaFornecedorNotaRepository.registrar_assinatura_nota(usuario_id, nota_id, dados_assinatura)
