# app/models/assinatura_nota_model.py
from app.extensions.database import db
from . import BaseModel

class AssinaturaNota(BaseModel):
    __tablename__ = 'assinatura_nota'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuario.id', ondelete='NO ACTION', name='FK_assinatura_nota_usuario'),
        nullable=True
    )
    nota_id = db.Column(
        db.Integer,
        db.ForeignKey('fornecedor_nota.id', ondelete='SET NULL', name='FK_assinatura_nota_fornecedor_nota'),
        nullable=True,
        unique=True
    )
    hash = db.Column(db.String(64), nullable=True)
    ip = db.Column(db.String(64), nullable=True)
    acao = db.Column(db.String(50), nullable=True)
    lote_id = db.Column(db.String(64), nullable=True)
    assinatura = db.Column(db.Text, nullable=True)

    # Relacionamentos
    usuario = db.relationship(
        'Usuario',
        backref=db.backref('assinatura_notas', lazy='dynamic')
    )
    nota = db.relationship(
        'FornecedorNota',
        back_populates='assinatura_nota'
    )

    __table_args__ = (
        db.Index('FK_assinatura_nota_fornecedor_nota', 'nota_id'),
        db.Index('FK_assinatura_nota_usuario', 'usuario_id'),
        db.UniqueConstraint('hash', 'ip', 'acao', name='uq_assinatura_nota_hash_ip_acao'),
    )
