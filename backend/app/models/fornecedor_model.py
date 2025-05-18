# app/models/fornecedor_model.py
from app.extensions.database import db
from . import BaseModel

class Fornecedor(BaseModel):
    __tablename__ = 'fornecedor'

    id = db.Column(db.Integer, primary_key=True)
    parceiro_cedente = db.Column(db.Boolean, default=False, nullable=False, server_default="0")
    razao_social = db.Column(db.String(255), nullable=False)
    nome_fantasia = db.Column(db.String(255), nullable=True)
    cpf_cnpj = db.Column(db.String(18), nullable=False)  # CPF ou CNPJ
    socio_representante = db.Column(db.String(255), nullable=True)
    cpf_representante = db.Column(db.String(255), nullable=True) 
    email_representante = db.Column(db.String(255), nullable=True)  # Email do responsável
    email = db.Column(db.String(255), nullable=True)  # Email do fornecedor
    telefone = db.Column(db.String(255), nullable=True)  # telefone do fornecedor

    cdcredor = db.Column(db.String(100), default='0')  # Código do credor
    tipo_pagamento = db.Column(db.String(100), nullable=True)  # Tipo de pagamento
    chavepix = db.Column(db.String(100), nullable=True)  # Chave PIX
    tipo_chave = db.Column(db.String(100), nullable=True)  # Tipo da chave PIX
    formulario = db.Column(db.Text, nullable=True)  # Formulário em formato JSON
    endereco = db.Column(db.String(100), nullable=True)  # Endereço
    compl = db.Column(db.String(255), nullable=True)  # Complemento
    bairro = db.Column(db.String(255), nullable=True)  # Bairro
    cep = db.Column(db.String(50), nullable=True)  # CEP
    municipio = db.Column(db.String(100), nullable=True)  # Município
    uf = db.Column(db.String(2), nullable=True)  # UF
    numero = db.Column(db.String(10), default=2)  # Número
    bco = db.Column(db.String(255), nullable=True)  # Banco
    agencia = db.Column(db.String(255), nullable=True)  # Agência
    conta = db.Column(db.String(255), nullable=True)  # Conta bancária
    
    # Relacionamento com FornecedorParceiro
    fornecedores_parceiros = db.relationship(
        'FornecedorParceiro',
        backref='fornecedor',
        cascade='all, delete-orphan'
    )
    notas = db.relationship(
        'FornecedorNota',
        back_populates='fornecedor',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    assinaturas_contrato_fornecedor = db.relationship(
        'AssinaturaContratoFornecedor',
        back_populates='fornecedor',
        overlaps="assinaturas_contrato,fornecedor_parceiro"
    )