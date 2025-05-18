from app.models.agendamento_model import Agendamento
from app.extensions.database import db

class AgendamentoRepository:
    @staticmethod
    def create(dados):
        try:
            agendamento = Agendamento(**dados)
            db.session.add(agendamento)
            db.session.commit()
            return agendamento
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Erro ao criar agendamento: {str(e)}")

    @staticmethod
    def get_by_id(agendamento_id):
        return Agendamento.query.get(agendamento_id)

    @staticmethod
    def get_by_parceiro_id(parceiro_id):
        return Agendamento.query.filter_by(parceiro_id=parceiro_id).all()
    
    @staticmethod
    def delete(agendamento_id):
        agendamento = Agendamento.query.get(agendamento_id)
        if agendamento:
            db.session.delete(agendamento)
            db.session.commit()
            return True
