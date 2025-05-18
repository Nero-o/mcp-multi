from flask import current_app
from app.extensions.database import db
from app.models.fornecedor_nota_parcela_model import FornecedorNotaParcela
from datetime import datetime

class FornecedorNotaParcelaRepository:
    
    # UPDATE
    @staticmethod
    def update_fornecedor_nota_parcela(parcela_id, dados):
        parcela = FornecedorNotaParcela.query.get(parcela_id)

        try:
            if parcela:
                if 'status_parcela_admin_id' in dados and dados['status_parcela_admin_id'] in [1, 4]:
                    dados['data_pagamento'] = datetime.now()
                
                for key, value in dados.items():
                    setattr(parcela, key, value)
                
                db.session.commit()
                return parcela
        except Exception as e:
            current_app.logger.error(f"Erro ao atualizar parcela: {str(e)}")
            db.session.rollback()

        return None 