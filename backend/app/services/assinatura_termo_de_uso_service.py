from app.repositories.assinatura_termo_de_uso_repository import AssinaturaTermoDeUsoRepository


class AssinaturaTermoDeUsoService:

    @staticmethod
    def get_assinatura_termo_de_uso(parceiro_id, fornecedor_id=None, usuario_id=None):
        return AssinaturaTermoDeUsoRepository.get_assinatura_termo_de_uso(parceiro_id, fornecedor_id, usuario_id)

    @staticmethod
    def registrar_assinatura_termo_de_uso(fornecedor_id, parceiro_id, usuario_id, dados_assinatura):
        return AssinaturaTermoDeUsoRepository.registrar_assinatura_termo_de_uso(fornecedor_id, parceiro_id, usuario_id, dados_assinatura)
