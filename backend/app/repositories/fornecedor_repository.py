from app.models.fornecedor_model import Fornecedor
from app.models.fornecedor_nota_model import FornecedorNota
from app.extensions.database import db
from flask import current_app
from sqlalchemy import func

class FornecedorRepository:

    # CREATE
    @staticmethod
    def create_fornecedor(dados):
        try:
            novo_fornecedor = Fornecedor(**dados)
            db.session.add(novo_fornecedor)
            db.session.commit()
            return novo_fornecedor
        except Exception as e:
            current_app.logger.error(f"Erro ao criar fornecedor {str(e)}")
            db.session.rollback()
            return False
        
    @staticmethod
    def get_fornecedor_por_id(fornecedor_id):
        return Fornecedor.query.get(fornecedor_id)

    # UPDATE
    @staticmethod
    def update_fornecedor(fornecedor_id, dados):
        fornecedor = Fornecedor.query.get(fornecedor_id)

        try:
            if fornecedor:
                for key, value in dados.items():
                    setattr(fornecedor, key, value)
                db.session.commit()
                return fornecedor
        except Exception as e:
            current_app.logger.error(f"Erro ao atualizar fornecedor {str(e)}")
            db.session.rollback()

        return None

    # DELETE
    @staticmethod
    def delete_fornecedor(fornecedor_id):
        fornecedor = Fornecedor.query.get(fornecedor_id)

        try:
            if fornecedor:
                db.session.delete(fornecedor)
                db.session.commit()
                return True
        except Exception as e:
            current_app.logger.error(f"Erro ao deletar fornecedor {str(e)}")
            db.session.rollback()

        return False

    @staticmethod
    def get_fornecedor_por_id(fornecedor_id):
        return Fornecedor.query.get(fornecedor_id)
    
    @staticmethod
    def get_fornecedor_por_nome(nome):
        return Fornecedor.query.filter_by(nome=nome).first()
    
    @staticmethod
    def get_fornecedor_por_email(email):
        return Fornecedor.query.filter_by(email=email).first()
    
    @staticmethod
    def get_all_fornecedor_por_email(email):
        return Fornecedor.query.filter_by(email=email).all()
    
    @staticmethod
    def get_fornecedor_por_cnpj(cnpj):
        return Fornecedor.query.filter_by(cnpj=cnpj).first()

    @staticmethod   
    def get_all_fornecedor(join_model=None, add_columns=None, filter=None):
        query = Fornecedor.query
        if join_model:
            query = query.join(join_model)
        if add_columns:
            query = query.add_columns(*add_columns)
        if filter is not None:
            query = query.filter(filter)
        return query
    
    @staticmethod
    def get_ultimas_notas(fornecedor_id, parceiro_id, limit=10):
        return FornecedorNota.query.filter_by(
            fornecedor_id=fornecedor_id,
            parceiro_id=parceiro_id
        ).order_by(FornecedorNota.id.desc()).limit(limit).all()

    @staticmethod
    def get_ultimas_notas_por_status(fornecedor_id, parceiro_id, status_id, limit=10):
        return FornecedorNota.query.filter_by(
            fornecedor_id=fornecedor_id,
            parceiro_id=parceiro_id,
            status_id=status_id
        ).order_by(FornecedorNota.id.desc()).limit(limit).all()
    


    @staticmethod
    def get_total_fornecedores(filter_by=None):
        query = db.session.query(func.count(Fornecedor.id))
        if filter_by:
            query = query.filter_by(**filter_by)
        return query.scalar()

    @staticmethod
    def get_ultimos_fornecedores(limit=10):
        fornecedores =  Fornecedor.query.order_by(Fornecedor.id.desc()).limit(limit).all()
        return [fornecedor.serialize() for fornecedor in fornecedores]
    
    @staticmethod
    def get_ultimos_fornecedores_por_status(excluido, limit=10):
        fornecedores = Fornecedor.query.filter_by(excluido=excluido).order_by(Fornecedor.id.desc()).limit(limit).all()
        return [fornecedor.serialize() for fornecedor in fornecedores]