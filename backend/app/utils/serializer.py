
class Serializer:

    @staticmethod
    def serialize_nota(result_tuple):
        fornecedor_nota, razao_social, cpf_cnpj = result_tuple
        serialized = fornecedor_nota.serialize()
        serialized['razao_social'] = razao_social
        serialized['cpf_cnpj'] = cpf_cnpj
        return serialized
    
    @staticmethod
    def serialize_usuario(item):
        usuario = item[0]  # Usuario instance
        parceiro_nome = item[1]
        parceiro_tenant_code = item[2]

        # Assuming Usuario has a serialize method
        usuario_data = usuario.serialize()
        usuario_data['parceiro_nome'] = parceiro_nome
        usuario_data['parceiro_tenant_code'] = parceiro_tenant_code

        return usuario_data

    @staticmethod
    def serialize_fornecedor(item):
        fornecedor = item[0]  # Instância de Fornecedor
        status = item[1]      # Campo 'status' (excluido) de FornecedorParceiro

        fornecedor_data = fornecedor.serialize()  # Ou fornecedor.to_dict()
        fornecedor_data['status'] = status

        return fornecedor_data
