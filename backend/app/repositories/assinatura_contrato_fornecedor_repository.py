from app.extensions.database import db
from app.models.assinatura_contrato_fornecedor_model import AssinaturaContratoFornecedor

class AssinaturaContratoFornecedorRepository:

    @staticmethod
    def get_assinatura_contrato_fornecedor(fornecedor_id, parceiro_id):
        return AssinaturaContratoFornecedor.query.filter_by(fornecedor_id=fornecedor_id, parceiro_id=parceiro_id).first()
    
    @staticmethod
    def registrar_assinatura_contrato_fornecedor(fornecedor_id, parceiro_id, dados_assinatura):
        assinatura_contrato_fornecedor = AssinaturaContratoFornecedor(fornecedor_id=fornecedor_id, parceiro_id=parceiro_id, **dados_assinatura)
        db.session.add(assinatura_contrato_fornecedor)
        db.session.commit()
        return assinatura_contrato_fornecedor