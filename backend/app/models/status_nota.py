# app/models/status_nota.py
from app.extensions.database import db
from . import BaseModel

class StatusNota(BaseModel):
    __tablename__ = 'status_nota'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    nome = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.String(255), nullable=True)