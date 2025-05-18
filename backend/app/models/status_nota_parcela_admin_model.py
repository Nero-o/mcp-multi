# app/models/status_nota_admin.py
from app.extensions.database import db
from . import BaseModel

# Status financeiro da parcela

class StatusNotaParcelaAdmin(BaseModel):
    __tablename__ = 'status_nota_parcela_admin'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    nome = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.String(255), nullable=True)

