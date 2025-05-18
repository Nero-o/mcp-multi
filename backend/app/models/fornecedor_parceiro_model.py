# app/models/fornecedor_parceiro_model.py
from app.extensions.database import db
from . import BaseModel

class FornecedorParceiro(BaseModel):
    __tablename__ = 'fornecedor_parceiro'

    fornecedor_id = db.Column(
        db.Integer,
        db.ForeignKey('fornecedor.id', name='fk_fornecedor_parceiro_fornecedor'),
        primary_key=True
    )
    parceiro_id = db.Column(
        db.Integer,
        db.ForeignKey('parceiro.id', name='fk_fornecedor_parceiro_parceiro'),
        primary_key=True
    )
    taxa_tac_lote = db.Column(db.Float, nullable=True)  # Taxa TAC
    taxa_tac_individual = db.Column(db.Float, nullable=True)  # Taxa TAC individual
    taxa_desconto_lote = db.Column(db.Float, nullable=True)  # Taxa personalizada
    taxa_desconto_individual = db.Column(db.Float, nullable=True)  # Taxa personalizada individual


    assinaturas_contrato = db.relationship(
        'AssinaturaContratoFornecedor',
        back_populates='fornecedor_parceiro',
        overlaps="assinaturas_contrato_fornecedor"
    )