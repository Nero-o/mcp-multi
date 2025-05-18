# app/models/assinatura_upload.py
from app.extensions.database import db
from . import BaseModel

class AssinaturaUpload(BaseModel):
    __tablename__ = 'assinatura_upload'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    parceiro_id = db.Column(db.Integer, db.ForeignKey('parceiro.id'), nullable=False)
    hash_upload = db.Column(db.Text, nullable=True)
    ip = db.Column(db.String(255), nullable=True)  
    assinatura = db.Column(db.Text, nullable=True)
    data_assinatura_upload = db.Column(db.DateTime, nullable=True)

    # Relacionamento com o modelo Usuario
    usuario = db.relationship('Usuario', backref=db.backref('assinatura_uploads', lazy=True))

    # Relacionamento com o modelo Parceiro
    parceiro = db.relationship('Parceiro', backref=db.backref('assinatura_uploads', lazy=True))
