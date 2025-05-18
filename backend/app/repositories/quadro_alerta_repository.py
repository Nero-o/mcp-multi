from app.models.quadro_alerta_model import QuadroAlerta
from app.extensions.database import db
from flask import current_app

class QuadroAlertaRepository:

    @staticmethod   
    def get_all_quadro_alerta(filter=None):
        # Inicia a query base
        query = QuadroAlerta.query

        if filter:
            query = query.filter_by(**filter)

        # Executa a consulta e retorna os resultados
        return query.all()

    @staticmethod
    def get_quadro_alerta_por_id(quadro_alerta_id):
        return QuadroAlerta.query.get(quadro_alerta_id)
    
    @staticmethod
    def get_quadro_alerta_por_usuario(usuario_id):
        return QuadroAlerta.query.filter_by(usuario_id=usuario_id).first()
    
    # CREATE
    @staticmethod
    def create_quadro_alerta(dados):
        try:
            novo_quadro_alerta = QuadroAlerta(**dados)
            db.session.add(novo_quadro_alerta)
            db.session.commit()
            return novo_quadro_alerta
        except Exception as e:
            current_app.logger.error(f"Erro ao criar quadro_alerta {str(e)}")
            db.session.rollback()
            return False
        

    # UPDATE
    @staticmethod
    def update_quadro_alerta(quadro_alerta_id, dados):
        try:
            quadro_alerta = QuadroAlerta.query.get(quadro_alerta_id)
            if quadro_alerta:
                for key, value in dados.items():
                    try:
                        setattr(quadro_alerta, key, value)
                    except Exception as e:
                        current_app.logger.error(f"Erro ao atualizar quadro_alerta {key}:{value} - {str(e)}")
                db.session.commit()
                return quadro_alerta
        except Exception as e:
            current_app.logger.error(f"Erro ao atualizar quadro_alerta {str(e)}")
            db.session.rollback()
        return None