# app/models/config_model.py
from app.extensions.database import db
from . import BaseModel

class ConfigModel(BaseModel):
    __tablename__ = 'config'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    prazo_maximo = db.Column(db.Integer)
    dias_ate_vencimento = db.Column(db.Integer)
    email_admin = db.Column(db.String(255), nullable=True)
    api_key = db.Column(db.String(255), nullable=True)
    opera_sacado = db.Column(db.Boolean, default=True)
    opera_cedente = db.Column(db.Boolean, default=False)
    tac_aeco = db.Column(db.Float, nullable=True)
    banco_aeco = db.Column(db.Float, nullable=True)
    taxa_mensal_aeco = db.Column(db.Float, nullable=True)

    parceiro_id = db.Column(
        db.Integer,
        db.ForeignKey('parceiro.id', ondelete='CASCADE'),
        unique=True,
        nullable=False
    )

    parceiro = db.relationship(
        'Parceiro',
        back_populates='config',
        passive_deletes=True,  # Adicionar esta linha
        cascade="all, delete"  # Modificar para incluir delete-orphan
    )
