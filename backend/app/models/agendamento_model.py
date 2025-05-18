from app.extensions.database import db
from . import BaseModel
from datetime import datetime

class Agendamento(BaseModel):
    __tablename__ = 'agendamento'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo_tarefa = db.Column(db.String(50), nullable=False)
    hora = db.Column(db.Time, nullable=False)
    dia_semana = db.Column(db.String(50), nullable=False)  # "1,2,3,4,5"
    parametros = db.Column(db.JSON)
    excluido = db.Column(db.Boolean, default=True) 
    
    # Relacionamentos
    parceiro_id = db.Column(
        db.Integer,
        db.ForeignKey('parceiro.id', ondelete='CASCADE'),
        nullable=False
    )
    config_id = db.Column(
        db.Integer,
        db.ForeignKey('config.id', ondelete='CASCADE'),
        nullable=False
    )

    config = db.relationship('ConfigModel', backref='agendamentos')
    historicos = db.relationship('AgendamentoHistorico', back_populates='agendamento')



class AgendamentoHistorico(BaseModel):
    __tablename__ = 'agendamento_historico'

    id = db.Column(db.Integer, primary_key=True)
    data_execucao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'sucesso', 'falha'
    mensagem = db.Column(db.Text)  # Mensagem de erro em caso de falha
    parametros_execucao = db.Column(db.JSON)  # Parâmetros usados na execução
    
    # Relacionamentos
    agendamento_id = db.Column(
        db.Integer,
        db.ForeignKey('agendamento.id', ondelete='CASCADE'),
        nullable=False
    )
    parceiro_id = db.Column(
        db.Integer,
        db.ForeignKey('parceiro.id', ondelete='CASCADE'),
        nullable=False
    )

    agendamento = db.relationship('Agendamento', back_populates='historicos')
