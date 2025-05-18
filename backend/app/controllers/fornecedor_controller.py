from flask import jsonify, g
from app.services.fornecedor_service import FornecedorService
from app.controllers.usuario_controller import UsuarioController
from app.services.parceiro_service import ParceiroService
from app.controllers.auth_controller import AuthController
from app.models.fornecedor_model import Fornecedor
from app.utils.paginacao import PaginacaoHelper
from app.utils.serializer import Serializer
class FornecedorController:

    @staticmethod
    def home(fornecedor_id):
        tenant_code = g.tenant_url

        dashboard_data = FornecedorService.get_dashboard_data(fornecedor_id, tenant_code)
        if not dashboard_data:
            return "Dados não encontrados", 404

        return jsonify(dashboard_data), 200
    
    # CREATE
    @staticmethod
    def create_fornecedor(dados):
        return FornecedorService.create_fornecedor(dados)
        
    @staticmethod
    def get_fornecedor_por_id(fornecedor_id):
        return FornecedorService.get_fornecedor_por_id(fornecedor_id)

    # UPDATE
    @staticmethod
    def update_fornecedor(fornecedor_id, dados):
        if 'confirmNewPassword' in dados and dados['confirmNewPassword'] and 'newPassword' in dados and dados['newPassword']:

            if dados['confirmNewPassword'] != dados['newPassword']:
                return jsonify({'error': 'Senhas não conferem.'}), 400
            
            if not 'oldPassword' in dados or not dados['oldPassword']:
                return jsonify({'error': 'Senha antiga não informada.'}), 400
            
            response, status_code = AuthController.alterar_senha_usuario(dados['oldPassword'], dados['newPassword'])

            if status_code != 200:
                return response, status_code
            
        fornecedor = FornecedorService.update_fornecedor(fornecedor_id, dados)

        return fornecedor.serialize(), 200

    # DELETE
    @staticmethod
    def delete_fornecedor(fornecedor_id):
        return FornecedorService.delete_fornecedor(fornecedor_id)

    @staticmethod
    def get_fornecedor_por_id(fornecedor_id):
        return FornecedorService.get_fornecedor_por_id(fornecedor_id)
    
    @staticmethod
    def get_fornecedor_por_nome(nome):
        return FornecedorService.get_fornecedor_por_nome(nome)
    
    @staticmethod
    def get_fornecedor_por_email(email):
        return FornecedorService.get_fornecedor_por_email(email)
    
    @staticmethod
    def get_fornecedor_por_cnpj(cnpj):
        return FornecedorService.get_fornecedor_por_cnpj(cnpj)



    @staticmethod
    def get_all_fornecedor(page, per_page, usuario_logado, tenant_url):

        if isinstance(usuario_logado['role'], list):
            role = usuario_logado['role'][0]
        else:
            role = usuario_logado['role']

        if role == 'Administrador':
            tenant = ParceiroService.get_parceiro_por_tenant(tenant_url)
            filter = Fornecedor.fornecedores_parceiros.any(parceiro_id=tenant.id)

        if role in ['Parceiro', 'ParceiroAdministrador']:
            usuario, mensagem = UsuarioController.valida_vinculo_usuario_parceiro_logado(usuario_logado, tenant_url)
            filter = Fornecedor.fornecedores_parceiros.any(parceiro_id=usuario.parceiro_id)

        query = FornecedorService.get_all_fornecedor(filter=filter)

        return PaginacaoHelper.paginate_query(
            query=query,
            page=page,
            per_page=per_page,
            serialize_func=Serializer.serialize_fornecedor
        )

