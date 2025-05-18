# app/services/fornecedor_service.py
from app.repositories.fornecedor_repository import FornecedorRepository
from app.repositories.parceiro_repository import ParceiroRepository
from app.models.fornecedor_parceiro_model import FornecedorParceiro
class FornecedorService:

    # CREATE
    @staticmethod
    def create_fornecedor(dados):
        return FornecedorRepository.create_fornecedor(dados)
        
    @staticmethod
    def get_fornecedor_por_id(fornecedor_id):
        return FornecedorRepository.get_fornecedor_por_id(fornecedor_id)

    # UPDATE
    @staticmethod
    def update_fornecedor(fornecedor_id, dados):
        return FornecedorRepository.update_fornecedor(fornecedor_id, dados)

    # DELETE
    @staticmethod
    def delete_fornecedor(fornecedor_id):
        return FornecedorRepository.delete_fornecedor(fornecedor_id)

    @staticmethod
    def get_fornecedor_por_nome(nome):
        return FornecedorRepository.get_fornecedor_por_nome(nome)
    
    @staticmethod
    def get_all_fornecedor_por_email(email):
        return FornecedorRepository.get_all_fornecedor_por_email(email)
    
    @staticmethod
    def get_fornecedor_por_email(email):
        return FornecedorRepository.get_fornecedor_por_email(email)
    
    @staticmethod
    def get_fornecedor_por_cnpj(cnpj):
        return FornecedorRepository.get_fornecedor_por_cnpj(cnpj)

    # READ
    @staticmethod
    def get_all_fornecedor(join_model=None, add_columns=None, filter=None):
        join_model = FornecedorParceiro
        add_columns = [FornecedorParceiro.excluido.label('status')]
        return FornecedorRepository.get_all_fornecedor(join_model=join_model, add_columns=add_columns, filter=filter)

