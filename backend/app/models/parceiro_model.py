# app/models/parceiro_model.py
from app.extensions.database import db
from . import BaseModel

class Parceiro(BaseModel):
    __tablename__ = 'parceiro'

    id = db.Column(db.Integer, primary_key=True)
    logo = db.Column(db.String(255))
    tenant_code = db.Column(db.String(255), nullable=False, unique=True)
    nome = db.Column(db.String(255), nullable=False)
    cpf_cnpj = db.Column(db.String(18), nullable=False)

    # Relacionamento com FornecedorParceiro
    fornecedores_parceiros = db.relationship(
        'FornecedorParceiro',
        backref='parceiro',
        cascade='all, delete-orphan'
    )

    # Relacionamento com ConfigModel
    config = db.relationship(
        'ConfigModel',
        back_populates='parceiro',
        cascade="all, delete-orphan"
    )

    assinaturas_contrato_fornecedor = db.relationship(
        'AssinaturaContratoFornecedor',
        foreign_keys='AssinaturaContratoFornecedor.parceiro_id',
        back_populates='parceiro',
        overlaps="assinaturas_contrato,fornecedor_parceiro"
    )