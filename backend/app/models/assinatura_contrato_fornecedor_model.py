# app/models/assinatura_contrato_fornecedor_model.py
from app.extensions.database import db
from . import BaseModel
from datetime import datetime

class AssinaturaContratoFornecedor(BaseModel):
    __tablename__ = 'assinatura_contrato_fornecedor'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    fornecedor_id = db.Column(
        db.Integer,
        db.ForeignKey('fornecedor.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False
    )
    parceiro_id = db.Column(
        db.Integer,
        db.ForeignKey('parceiro.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False
    )
    hash_contrato = db.Column(db.String(64), nullable=True)
    ip = db.Column(db.Text, nullable=True)
    assinatura = db.Column(db.Text, nullable=True)
    data_assinatura_contrato = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.Index('idx_assinatura_contrato_fornecedor', 'fornecedor_id', 'parceiro_id'),
        db.UniqueConstraint('hash_contrato', name='uq_assinatura_contrato_fornecedor_hashes'),
        db.ForeignKeyConstraint(
            ['fornecedor_id', 'parceiro_id'],
            ['fornecedor_parceiro.fornecedor_id', 'fornecedor_parceiro.parceiro_id'],
            ondelete='CASCADE',
            onupdate='CASCADE'
        ),
    )

    # Relationships
    fornecedor_parceiro = db.relationship(
        'FornecedorParceiro',
        back_populates='assinaturas_contrato',
        overlaps="fornecedor,parceiro"
    )

    fornecedor = db.relationship(
        'Fornecedor',
        foreign_keys=[fornecedor_id],
        back_populates='assinaturas_contrato_fornecedor',
        overlaps="fornecedor_parceiro,assinaturas_contrato"
    )

    parceiro = db.relationship(
        'Parceiro',
        foreign_keys=[parceiro_id],
        back_populates='assinaturas_contrato_fornecedor',
        overlaps="fornecedor_parceiro,assinaturas_contrato"
    )