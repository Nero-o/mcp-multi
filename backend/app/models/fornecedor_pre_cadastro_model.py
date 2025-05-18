from app.extensions.database import db
from . import BaseModel
from datetime import datetime

class FornecedorPreCadastro(BaseModel):
    __tablename__ = 'fornecedor_pre_cadastro'

    id = db.Column(db.Integer, primary_key=True)
    razao_social = db.Column(db.String(255), nullable=False)
    nome_fantasia = db.Column(db.String(255), nullable=False)
    cpf_cnpj = db.Column(db.String(18), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(255), nullable=False)
    nome_representante = db.Column(db.String(255), nullable=False)
    cpf_representante = db.Column(db.String(14), nullable=False)
    email_representante = db.Column(db.String(255), nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    complemento = db.Column(db.String(255), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    cep = db.Column(db.String(8), nullable=False)
    pais = db.Column(db.String(100), nullable=False, default='Brasil')
    fonte_conhecimento = db.Column(db.String(255), nullable=False)
    
    # Campos para rastreamento
    status = db.Column(db.String(50), default='pendente')  # pendente, aprovado, rejeitado
    observacoes = db.Column(db.Text, nullable=True)
    data_pre_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ip_cadastro = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)