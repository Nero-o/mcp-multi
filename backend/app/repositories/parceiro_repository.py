from sqlalchemy import func
from flask import current_app
from app.models.parceiro_model import Parceiro
from app.models.fornecedor_model import Fornecedor
from app.models.fornecedor_nota_model import FornecedorNota
from app.models.fornecedor_parceiro_model import FornecedorParceiro
from app.extensions.database import db

class ParceiroRepository:

    

    @staticmethod
    def get_total_parceiros():
        return db.session.query(func.count(Parceiro.id)).scalar()
    
    # CREATE
    @staticmethod
    def create_parceiro(dados):
        try:
            campos_validos = {}
            colunas_parceiro = Parceiro.__table__.columns.keys()
            
            for chave, valor in dados.items():
                if chave in colunas_parceiro and chave != 'data_cadastro' and chave != 'data_alteracao':
                    campos_validos[chave] = valor
                    
            novo_parceiro = Parceiro(**campos_validos)
            db.session.add(novo_parceiro)
            db.session.commit()
            return novo_parceiro
        except Exception as e:
            current_app.logger.error(f"Erro ao criar parceiro {str(e)}")
            db.session.rollback()
            return False
        
    @staticmethod
    def get_parceiro_por_tenant(tenant):
        return Parceiro.query.filter_by(tenant_code=tenant).first()
    
    @staticmethod
    def get_total_fornecedores(parceiro_id):
        return db.session.query(func.count(Fornecedor.id)).\
            join(FornecedorParceiro, Fornecedor.id == FornecedorParceiro.fornecedor_id).\
            filter(FornecedorParceiro.parceiro_id == parceiro_id).scalar()

    @staticmethod
    def get_total_notas(parceiro_id):
        return db.session.query(func.count(FornecedorNota.id)).\
            filter(FornecedorNota.parceiro_id == parceiro_id).scalar()

    @staticmethod
    def get_ultimas_notas(parceiro_id, limit=10):
        return FornecedorNota.query.filter_by(parceiro_id=parceiro_id).order_by(FornecedorNota.id.desc()).limit(limit).all()

    @staticmethod
    def get_ultimas_notas_por_status(parceiro_id, status_id, limit=10):
        return FornecedorNota.query.filter_by(parceiro_id=parceiro_id, status_id=status_id).order_by(FornecedorNota.id.desc()).limit(limit).all()
    # READ
    @staticmethod
    def get_all_parceiro():
        return Parceiro.query

    @staticmethod
    def get_parceiro_por_id(parceiro_id):
        return Parceiro.query.get(parceiro_id)

    # UPDATE
    @staticmethod
    def update_parceiro(parceiro_id, dados):
        try:
            parceiro = Parceiro.query.get(parceiro_id)
            if parceiro:
                for key, value in dados.items():
                    setattr(parceiro, key, value)
                db.session.commit()
                return parceiro
        except Exception as e:
            current_app.logger.error(f"Erro ao atualizar parceiro {str(e)}")
            db.session.rollback()
        return None

    # DELETE
    @staticmethod
    def delete_parceiro(parceiro_id):
        parceiro = Parceiro.query.get(parceiro_id)
        try:
            if parceiro:
                db.session.delete(parceiro)
                db.session.commit()
                return True
        except Exception as e:
            current_app.logger.error(f"Erro ao deletar parceiro {str(e)}")
            db.session.rollback()
        return False
