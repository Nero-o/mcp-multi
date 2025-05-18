from app.models.fornecedor_parceiro_model import FornecedorParceiro
from app.models.fornecedor_nota_model import FornecedorNota
from app.models.fornecedor_model import Fornecedor
from sqlalchemy import func
from app.extensions.database import db
from flask import current_app

class FornecedorParceiroRepository:
    
    @staticmethod
    def count_fornecedores_por_status(parceiro_id, excluido):
        return FornecedorParceiro.query.filter(
            FornecedorParceiro.parceiro_id == parceiro_id,
            FornecedorParceiro.excluido == excluido
        ).count()
    
    @staticmethod
    def get_top_fornecedores_por_valor(parceiro_id, status_ids, limit= 5):        
        
        top_fornecedores = db.session.query(
            FornecedorParceiro.fornecedor_id,
            Fornecedor.razao_social,
            func.sum(FornecedorNota.vlr_disp_antec).label('valorTotalAntecipado')
        ).join(
            Fornecedor, FornecedorParceiro.fornecedor_id == Fornecedor.id
        ).join(
            FornecedorNota, FornecedorParceiro.fornecedor_id == FornecedorNota.fornecedor_id
        ).filter(
            FornecedorParceiro.parceiro_id == parceiro_id,
            FornecedorParceiro.excluido == False,
            FornecedorNota.status_id.in_(status_ids)
        ).group_by(
            FornecedorParceiro.fornecedor_id,
            Fornecedor.razao_social
        ).order_by(
            func.sum(FornecedorNota.vlr_disp_antec).desc()
        ).limit(limit).all()

        return top_fornecedores
    
    @staticmethod
    def get_fornecedor_parceiro(parceiro_id, fornecedor_id):
        return FornecedorParceiro.query.filter_by(
            parceiro_id=parceiro_id,
            fornecedor_id=fornecedor_id
        ).first()

    @staticmethod
    def get_fornecedor_parceiro_por_parceiro_id(parceiro_id, excluido=None):
        if excluido:
            return FornecedorParceiro.query.filter_by(parceiro_id=parceiro_id, excluido=excluido).all()
        else:
            return FornecedorParceiro.query.filter_by(parceiro_id=parceiro_id).all()
        
    # UPDATE INDIVIDUAL
    @staticmethod
    def update_fornecedor_parceiro_individual(fornecedor_id, parceiro_id, dados):
        try:
            fornecedor_parceiros = FornecedorParceiro.query.filter_by(parceiro_id=parceiro_id, fornecedor_id=fornecedor_id).all()
            if fornecedor_parceiros:
                for parceiro in fornecedor_parceiros:
                    for key, value in dados.items():
                        setattr(parceiro, key, value)
                db.session.commit()
                return fornecedor_parceiros
            else:
                return None
        except Exception as e:
            current_app.logger.error(f"Erro ao atualizar fornecedor parceiro: {str(e)}")
            db.session.rollback()
        return None
    
    # UPDATE LOTE
    @staticmethod
    def update_fornecedor_parceiro_lote(parceiro_id, dados):
        try:
            fornecedor_parceiros = FornecedorParceiro.query.filter_by(parceiro_id=parceiro_id).all()
            if fornecedor_parceiros:
                for parceiro in fornecedor_parceiros:
                    for key, value in dados.items():
                        setattr(parceiro, key, value)
                db.session.commit()
                return fornecedor_parceiros
        except Exception as e:
            current_app.logger.error(f"Erro ao atualizar fornecedor parceiro: {str(e)}")
            db.session.rollback()
        return None
