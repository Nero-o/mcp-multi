from app.repositories.fornecedor_nota_repository import FornecedorNotaRepository

class FornecedorNotaService:

    @staticmethod
    def get_parcelas(nota_id):
        return FornecedorNotaRepository.get_parcelas(nota_id)

    @staticmethod   
    def get_all_fornecedor_nota_join(join_model, add_columns, filter, join_on=None):
        return FornecedorNotaRepository.get_all_fornecedor_nota_join(join_model, add_columns, filter, join_on)

    @staticmethod
    def nota_disponivel(nota):
        if nota.status_id in ('1', 1):
            return True
        return False

    @staticmethod
    def get_total_rows():
        return FornecedorNotaRepository.get_total_rows(filters=None)
    
    # READ
    @staticmethod
    def get_all_fornecedor_nota(limit=None, offset=None):
        return FornecedorNotaRepository.get_all_fornecedor_nota(limit, offset)
    
    # READ
    @staticmethod
    def get_all_fornecedor_nota_fornecedor(fornecedor_id, limit=None, offset=None):
        return FornecedorNotaRepository.get_all_fornecedor_nota_fornecedor(fornecedor_id=fornecedor_id, limit=limit, offset=offset)

    # CREATE
    @staticmethod
    def create_fornecedor_nota(dados):
        return FornecedorNotaRepository.create_fornecedor_nota(dados)
    
    @staticmethod
    def get_fornecedor_nota_por_id(fornecedor_nota_id):
        return FornecedorNotaRepository.get_fornecedor_nota_por_id(fornecedor_nota_id)
    

    @staticmethod
    def get_fornecedor_nota_por_multiplos_ids(fornecedor_nota_ids):
        return FornecedorNotaRepository.get_fornecedor_nota_por_multiplos_ids(fornecedor_nota_ids)

    @staticmethod
    def get_fornecedor_nota_por_id_join_fornecedor(fornecedor_nota_id, parceiro_id=None, fornecedor_id=None):
        return FornecedorNotaRepository.get_fornecedor_nota_por_id_join_fornecedor(fornecedor_nota_id, parceiro_id, fornecedor_id)
    
    # UPDATE
    @staticmethod
    def update_fornecedor_nota(fornecedor_nota_id, dados):
        return FornecedorNotaRepository.update_fornecedor_nota(fornecedor_nota_id, dados)

    # DELETE
    @staticmethod
    def delete_fornecedor_nota(fornecedor_nota_id):
        return FornecedorNotaRepository.delete_fornecedor_nota(fornecedor_nota_id)
