from app.extensions.database import db
from app.models.assinatura_termo_de_uso_model import AssinaturaTermoDeUso

class AssinaturaTermoDeUsoRepository:

    @staticmethod
    def get_assinatura_termo_de_uso(parceiro_id, fornecedor_id=None, usuario_id=None):
        query = AssinaturaTermoDeUso.query.filter_by(parceiro_id=parceiro_id, usuario_id=usuario_id)
        if fornecedor_id is not None:
            query = query.filter_by(fornecedor_id=fornecedor_id)
        else:
            query = query.filter(AssinaturaTermoDeUso.fornecedor_id.is_(None))
        return query.first()

    @staticmethod
    def registrar_assinatura_termo_de_uso(fornecedor_id, parceiro_id, usuario_id, dados_assinatura):
        assinatura_termo_de_uso = AssinaturaTermoDeUso(
            fornecedor_id=fornecedor_id,
            parceiro_id=parceiro_id,
            usuario_id=usuario_id,
            **dados_assinatura
        )
        db.session.add(assinatura_termo_de_uso)
        db.session.commit()
        return assinatura_termo_de_uso
