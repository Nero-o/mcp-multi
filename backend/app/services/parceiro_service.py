# parceiro_service.py
from app.repositories.parceiro_repository import ParceiroRepository
from flask import current_app

class ParceiroService():
    # CREATE
    @staticmethod
    def create_parceiro(dados):
        return ParceiroRepository.create_parceiro(dados)
    
    # UPDATE
    @staticmethod
    def update_parceiro(parceiro_id, dados):
        return ParceiroRepository.update_parceiro(parceiro_id, dados)
    
    # DELETE
    @staticmethod
    def delete_parceiro(parceiro_id):
        return ParceiroRepository.delete_parceiro(parceiro_id)
    
    ## GET
    @staticmethod
    def get_all_parceiro():
        all = ParceiroRepository.get_all_parceiro()
        return all
    
    @staticmethod
    def get_parceiro_por_id(parceiro_id):
        return ParceiroRepository.get_parceiro_por_id(parceiro_id)
    @staticmethod
    def get_parceiro_por_tenant(tenant):
        return ParceiroRepository.get_parceiro_por_tenant(tenant)


