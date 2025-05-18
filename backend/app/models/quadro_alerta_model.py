from app.extensions.database import db
from . import BaseModel
from sqlalchemy import Enum
from datetime import datetime

class QuadroAlerta(BaseModel):
    __tablename__ = 'quadro_alerta'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # Ex: 'upload', 'lembrete', 'sistema'
    data_expiracao = db.Column(db.DateTime, nullable=True)
    link = db.Column(db.String(255), nullable=True)
    dados_extras = db.Column(db.Text, nullable=True)

    destinatario_tipo = db.Column(
        Enum('usuario', 'role', 'fornecedor', 'parceiro', 'todos', name='destinatario_tipo_enum'),
        nullable=False,
        default='usuario'
    )

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    role = db.Column(db.String(50), nullable=True)
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedor.id', name='fk_quadro_alerta_fornecedor'), nullable=True)
    parceiro_id = db.Column(db.Integer, db.ForeignKey('parceiro.id'), nullable=True)

    # Relacionamentos
    usuario = db.relationship('Usuario', backref='alertas_usuario', foreign_keys=[usuario_id])
    fornecedor = db.relationship('Fornecedor', backref='alertas_fornecedor')
    parceiro = db.relationship('Parceiro', backref='alertas_parceiro')
