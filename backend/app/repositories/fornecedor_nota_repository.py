from flask import current_app
from sqlalchemy import and_
from app.extensions.database import db
from app.models.fornecedor_nota_model import FornecedorNota
from app.models.fornecedor_model import Fornecedor
from app.models.fornecedor_nota_parcela_model import FornecedorNotaParcela

class FornecedorNotaRepository:

    @staticmethod
    def get_parcelas(nota_id):
        return FornecedorNotaParcela.query.filter(FornecedorNotaParcela.operacao_id == nota_id).all()

    @staticmethod   
    def get_all_fornecedor_nota_join(join_model, add_columns, filter=None, join_on=None):
        query = FornecedorNota.query
        if join_model:
            if join_on:
                query = query.join(join_model, join_on)
            else:
                query = query.join(join_model)
            if add_columns:
                query = query.add_columns(*add_columns)

        if filter is not None:
            query = query.filter(filter)
        return query

    @staticmethod
    def get_total_count(filters=None):
        """
        Retorna o número total de FornecedorNotas aplicando os filtros fornecidos.
        """
        query = FornecedorNota.query
        if filters:
            query = query.filter_by(**filters)
        return query.count()

    @staticmethod
    def get_ultimas_notas(limit=10):
        notas= FornecedorNota.query.order_by(FornecedorNota.id.desc()).limit(limit).all()
        return [nota.serialize() for nota in notas]

    @staticmethod
    def get_ultimas_notas_por_status(status_id, limit=10):
        notas =  FornecedorNota.query.filter(FornecedorNota.status_id == status_id).order_by(FornecedorNota.id.desc()).limit(limit).all()
        return [nota.serialize() for nota in notas]

    # CREATE
    @staticmethod
    def create_fornecedor_nota(dados):
        try:
            novo_fornecedor_nota = FornecedorNota(**dados)
            db.session.add(novo_fornecedor_nota)
            db.session.commit()
            return novo_fornecedor_nota
        except Exception as e:
            current_app.logger.error(f"Erro ao criar fornecedor_nota {str(e)}")
            db.session.rollback()
            return False
        

    # UPDATE
    @staticmethod
    def update_fornecedor_nota(fornecedor_nota_id, dados):
        fornecedor_nota = FornecedorNota.query.get(fornecedor_nota_id)

        try:
            if fornecedor_nota:
                for key, value in dados.items():
                    setattr(fornecedor_nota, key, value)
                db.session.commit()
                return fornecedor_nota
        except Exception as e:
            current_app.logger.error(f"Erro ao atualizar fornecedor_nota {str(e)}")
            db.session.rollback()

        return None

    # DELETE
    @staticmethod
    def delete_fornecedor_nota(fornecedor_nota_id):
        fornecedor_nota = FornecedorNota.query.get(fornecedor_nota_id)

        try:
            if fornecedor_nota:
                db.session.delete(fornecedor_nota)
                db.session.commit()
                return True
        except Exception as e:
            current_app.logger.error(f"Erro ao deletar fornecedor_nota {str(e)}")
            db.session.rollback()

        return False

    @staticmethod
    def get_fornecedor_nota_por_id(fornecedor_nota_id):
        return FornecedorNota.query.get(fornecedor_nota_id)
    

    @staticmethod
    def get_fornecedor_nota_por_multiplos_ids(fornecedor_nota_ids):
        return FornecedorNota.query.filter(FornecedorNota.id.in_(fornecedor_nota_ids)).all()
    
    @staticmethod
    def get_fornecedor_nota_por_id_join_fornecedor(fornecedor_nota_id, parceiro_id=None, fornecedor_id=None): 
        query = FornecedorNota.query
        query_join = query.join(Fornecedor, FornecedorNota.fornecedor_id == Fornecedor.id) \
            .add_columns(Fornecedor.razao_social, Fornecedor.cpf_cnpj)

        # Start with the mandatory filter
        and_filter = [FornecedorNota.id == fornecedor_nota_id]

        # Add fornecedor_id filter if provided
        if fornecedor_id is not None:
            and_filter.append(FornecedorNota.fornecedor_id == fornecedor_id)

        # Add parceiro_id filter if provided
        if parceiro_id is not None:
            and_filter.append(FornecedorNota.parceiro_id == parceiro_id)

        return query_join.filter(and_(*and_filter))
         

    # READ
    @staticmethod
    def get_all_fornecedor_nota(limit=None, offset=None, **filters):
        # Inicia a query base
        query = FornecedorNota.query

        if filters:
            query = query.filter_by(**filters)
        
        # Aplica limite e offset se fornecidos
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        
        # Executa a consulta e retorna os resultados
        return query.all()

    # READ
    @staticmethod
    def get_all_fornecedor_nota_fornecedor(fornecedor_id, parceiro_id=None, limit=None, offset=None):
        # Inicia a query base
        query = FornecedorNota.query
        if not fornecedor_id:
            raise ValueError('Nenhum fornecedor informado.')
        query = query.filter(fornecedor_id=fornecedor_id)
        
        if parceiro_id:
            query = query.filter(parceiro_id=parceiro_id)
        # Aplica limite e offset se fornecidos
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        return query.all()

