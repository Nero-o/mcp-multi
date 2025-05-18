# app/models/fornecedor_nota_parcela.py
from app.extensions.database import db
from . import BaseModel
from datetime import datetime

class FornecedorNotaParcela(BaseModel):
    __tablename__ = 'fornecedor_nota_parcela'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    
    operacao_id = db.Column(
        db.Integer,
        db.ForeignKey('fornecedor_nota.id', ondelete='CASCADE', name='FK_fornecedor_nota_parcela_operacao'),
        nullable=False
    )
    
    status_parcela_id = db.Column(
        db.Integer,
        db.ForeignKey('status_nota_parcela.id', name='FK_fornecedor_nota_parcela_status'),
        nullable=True,
        default=None
    )
    
    status_parcela_admin_id = db.Column(
        db.Integer,
        db.ForeignKey('status_nota_parcela_admin.id', name='FK_fornecedor_nota_parcela_status_admin'),
        nullable=True,
        default=None
    )
    
    data_vencimento = db.Column(db.Date, nullable=False)
    data_pagamento = db.Column(db.Date, nullable=True)
    valor = db.Column(db.Float, nullable=False)

    
    # Relacionamentos
    operacao = db.relationship(
        'FornecedorNota',
        backref=db.backref('parcelas', cascade='all, delete-orphan', lazy='dynamic')
    )
    
    status_parcela = db.relationship(
        'StatusNotaParcela',
        foreign_keys=[status_parcela_id],
        backref=db.backref('parcelas', lazy='dynamic')
    )
    
    status_parcela_admin = db.relationship(
        'StatusNotaParcelaAdmin',
        foreign_keys=[status_parcela_admin_id],
        backref=db.backref('parcelas', lazy='dynamic')
    )