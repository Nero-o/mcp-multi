# app/models/usuario_model.py
from app.extensions.database import db
from . import BaseModel

class Usuario(BaseModel):
    __tablename__ = 'usuario'
    
    id = db.Column(db.Integer, primary_key=True) 
    idpUserId = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    senha_temporaria = db.Column(db.String(12), nullable=True)
    
    email_primeiro_acesso = db.Column(db.Boolean, nullable=False, default=False)
    assinatura_termo_de_uso = db.Column(db.Boolean, nullable=False, default=False)
    assinatura_contrato = db.Column(db.Boolean, nullable=False, default=False)

    fornecedor_id = db.Column(
        db.Integer,
        db.ForeignKey('fornecedor.id', name="fk_fornecedor_usuario"),
        nullable=True
    )
    parceiro_id = db.Column(
        db.Integer,
        db.ForeignKey('parceiro.id', name="fk_parceiro_usuario"),
        nullable=True
    )
