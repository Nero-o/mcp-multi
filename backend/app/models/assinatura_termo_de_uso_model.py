from app.extensions.database import db
from . import BaseModel
from datetime import datetime

class AssinaturaTermoDeUso(BaseModel):
    __tablename__ = 'assinatura_termo_de_uso'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    fornecedor_id = db.Column(db.Integer, nullable=True)
    parceiro_id = db.Column(db.Integer, nullable=False)
    usuario_id = db.Column(db.Integer, nullable=False)

    hash_termo = db.Column(db.String(64), nullable=True)
    ip = db.Column(db.Text, nullable=True)
    assinatura = db.Column(db.Text, nullable=True)
    data_assinatura_termo = db.Column(db.DateTime, nullable=True)

    # Relacionamentos
    fornecedor = db.relationship(
        'Fornecedor',
        backref=db.backref('assinaturas_termo_de_uso', lazy='dynamic'),
        primaryjoin='AssinaturaTermoDeUso.fornecedor_id == Fornecedor.id',
        foreign_keys=[fornecedor_id]
    )

    parceiro = db.relationship(
        'Parceiro',
        backref=db.backref('assinaturas_termo_de_uso', lazy='dynamic'),
        primaryjoin='AssinaturaTermoDeUso.parceiro_id == Parceiro.id',
        foreign_keys=[parceiro_id]
    )

    usuario = db.relationship(
        'Usuario',
        backref=db.backref('assinaturas_termo_de_uso', lazy='dynamic'),
        primaryjoin='AssinaturaTermoDeUso.usuario_id == Usuario.id',
        foreign_keys=[usuario_id]
    )

    __table_args__ = (
        db.ForeignKeyConstraint(
            ['parceiro_id'],
            ['parceiro.id'],
            name='fk_assinatura_termo_de_uso_parceiro',
            ondelete='CASCADE',
            onupdate='CASCADE'
        ),
        db.ForeignKeyConstraint(
            ['fornecedor_id'],
            ['fornecedor.id'],
            name='fk_assinatura_termo_de_uso_fornecedor',
            ondelete='CASCADE',
            onupdate='CASCADE'
        ),
        db.ForeignKeyConstraint(
            ['usuario_id'],
            ['usuario.id'],
            name='fk_assinatura_termo_de_uso_usuario',
            ondelete='CASCADE',
            onupdate='CASCADE'
        ),
        db.Index('idx_assinatura_termo_de_uso', 'fornecedor_id', 'parceiro_id', 'usuario_id'),
        db.UniqueConstraint('hash_termo', name='uq_assinatura_termo_de_uso_hashes'),
    )
