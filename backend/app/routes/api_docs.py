from flask import Blueprint, jsonify
from flask_restx import Resource, Namespace, fields
from app.extensions.restx_api import api
import logging

logger = logging.getLogger(__name__)

try:
    # Create blueprint
    api_docs_bp = Blueprint('api_docs', __name__)

    # Create and register namespaces
    namespaces = [
        ('auth', 'Operações de autenticação'),
        ('upload', 'Operações de upload de arquivos'),
        ('home', 'Operações da página inicial'),
        ('notas', 'Operações relacionadas a notas'),
        ('fornecedor-parceiro', 'Operações de gestão de fornecedores e taxas'),
    ]

    # Create namespace references
    auth_ns = None
    upload_ns = None
    home_ns = None
    notas_ns = None
    fornecedor_parceiro_ns = None

    for ns_name, ns_description in namespaces:
        try:
            ns = Namespace(ns_name, description=ns_description)
            api.add_namespace(ns)
            # Store namespace references
            if ns_name == 'auth':
                auth_ns = ns
            elif ns_name == 'upload':
                upload_ns = ns
            elif ns_name == 'home':
                home_ns = ns
            elif ns_name == 'notas':
                notas_ns = ns
            elif ns_name == 'fornecedor-parceiro':
                fornecedor_parceiro_ns = ns
        except Exception as e:
            logger.error(f"Error registering namespace {ns_name}: {str(e)}")

            raise

    # Add route to serve swagger.json for frontend
    @api_docs_bp.route('/swagger.json', methods=['GET'])
    def swagger_json():
        """Retorna o Swagger JSON para consumo pelo frontend"""
        return jsonify(api.__schema__)

except Exception as e:
    logger.error(f"Error initializing API documentation: {str(e)}")
    logger.error("Error traceback:", exc_info=True)
    raise

# Models
taxa_model = api.model('Taxa', {
    'taxa': fields.Float(required=True, description='Valor da taxa a ser aplicada')
})

ativa_desativa_model = api.model('AtivaDesativa', {
    'ativo': fields.Boolean(required=True, description='Status de ativação do fornecedor')
})

upload_json_model = api.model('UploadJSON', {
    'data': fields.List(fields.Raw, description='Lista de dados a serem importados')
})

nota_model = api.model('Nota', {
    'fornecedor_id': fields.Integer(description='ID do fornecedor'),
    'valor': fields.Float(description='Valor da nota'),
    'data_vencimento': fields.String(description='Data de vencimento'),
    'status': fields.Integer(description='Status da nota')
})

login_model = api.model('Login', {
    'username': fields.String(required=True, description='Nome de usuário'),
    'password': fields.String(required=True, description='Senha do usuário')
})

# Documentação Home
@home_ns.route('/dashboard')
class Dashboard(Resource):
    @home_ns.doc('get_dashboard',
        description='Retorna dados consolidados do dashboard',
        responses={
            200: 'Dados retornados com sucesso',
            401: 'Não autorizado'
        })
    def get(self):
        """Retorna dados consolidados do dashboard"""
        pass

# Documentação Upload
@upload_ns.route('/upload-json')
class UploadJSON(Resource):
    @upload_ns.doc('upload_json',
        description='Upload de dados via JSON',
        responses={
            200: 'Upload realizado com sucesso',
            400: 'Erro na validação dos dados',
            401: 'Não autorizado'
        })
    @upload_ns.expect(upload_json_model)
    def post(self):
        """Realiza upload de dados estruturados via JSON"""
        pass

@upload_ns.route('/upload')
class UploadCSV(Resource):
    @upload_ns.doc('upload_csv',
        description='Upload de dados via arquivo CSV',
        responses={
            200: 'Upload realizado com sucesso',
            400: 'Erro no arquivo',
            401: 'Não autorizado'
        })
    def post(self):
        """Realiza upload de dados via arquivo CSV"""
        pass

# Documentação Fornecedor Parceiro
@fornecedor_parceiro_ns.route('/ativa_desativa_fornecedor')
class AtivaDesativaFornecedor(Resource):
    @fornecedor_parceiro_ns.doc('ativa_desativa_fornecedor',
        description='Ativa ou desativa um fornecedor',
        params={'fornecedor_id': 'ID do fornecedor'},
        responses={
            200: 'Status alterado com sucesso',
            400: 'Dados inválidos',
            401: 'Não autorizado'
        })
    @fornecedor_parceiro_ns.expect(ativa_desativa_model)
    def post(self):
        """Altera o status de ativação de um fornecedor"""
        pass

@fornecedor_parceiro_ns.route('/update_taxa_desconto_lote_fornecedor')
class UpdateTaxaDescontoLote(Resource):
    @fornecedor_parceiro_ns.doc('update_taxa_desconto_lote',
        description='Atualiza taxa de desconto em lote',
        responses={
            200: 'Taxa atualizada com sucesso',
            400: 'Dados inválidos',
            401: 'Não autorizado'
        })
    @fornecedor_parceiro_ns.expect(taxa_model)
    def post(self):
        """Atualiza a taxa de desconto para todos os fornecedores"""
        pass

@fornecedor_parceiro_ns.route('/update_taxa_tac_lote_fornecedor')
class UpdateTaxaTacLote(Resource):
    @fornecedor_parceiro_ns.doc('update_taxa_tac_lote',
        description='Atualiza taxa TAC em lote',
        responses={
            200: 'Taxa atualizada com sucesso',
            400: 'Dados inválidos',
            401: 'Não autorizado'
        })
    @fornecedor_parceiro_ns.expect(taxa_model)
    def post(self):
        """Atualiza a taxa TAC para todos os fornecedores"""
        pass

@fornecedor_parceiro_ns.route('/update_taxa_desconto_individual_fornecedor')
class UpdateTaxaDescontoIndividual(Resource):
    @fornecedor_parceiro_ns.doc('update_taxa_desconto_individual',
        description='Atualiza taxa de desconto individual',
        params={'fornecedor_id': 'ID do fornecedor'},
        responses={
            200: 'Taxa atualizada com sucesso',
            400: 'Dados inválidos',
            401: 'Não autorizado'
        })
    @fornecedor_parceiro_ns.expect(taxa_model)
    def post(self):
        """Atualiza a taxa de desconto para um fornecedor específico"""
        pass

@fornecedor_parceiro_ns.route('/update_taxa_tac_individual_fornecedor')
class UpdateTaxaTacIndividual(Resource):
    @fornecedor_parceiro_ns.doc('update_taxa_tac_individual',
        description='Atualiza taxa TAC individual',
        params={'fornecedor_id': 'ID do fornecedor'},
        responses={
            200: 'Taxa atualizada com sucesso',
            400: 'Dados inválidos',
            401: 'Não autorizado'
        })
    @fornecedor_parceiro_ns.expect(taxa_model)
    def post(self):
        """Atualiza a taxa TAC para um fornecedor específico"""
        pass

# Documentação Notas
@notas_ns.route('/lista_fornecedor_nota')
class ListaNotas(Resource):
    @notas_ns.doc('lista_notas',
        description='Lista todas as notas disponíveis',
        params={
            'page': 'Número da página',
            'per_page': 'Itens por página'
        },
        responses={
            200: 'Lista retornada com sucesso',
            400: 'Erro na requisição',
            401: 'Não autorizado'
        })
    def get(self):
        """Lista todas as notas disponíveis de forma paginada"""
        pass

@notas_ns.route('/lista_extrato_nota')
class ListaExtrato(Resource):
    @notas_ns.doc('lista_extrato',
        description='Lista o extrato de notas',
        params={
            'page': 'Número da página',
            'per_page': 'Itens por página'
        },
        responses={
            200: 'Extrato retornado com sucesso',
            400: 'Erro na requisição',
            401: 'Não autorizado'
        })
    def get(self):
        """Lista o extrato de notas de forma paginada"""
        pass

@notas_ns.route('/arquivo_retorno')
class ArquivoRetorno(Resource):
    @notas_ns.doc('arquivo_retorno',
        description='Gera arquivo de retorno',
        responses={
            200: 'Arquivo gerado com sucesso',
            400: 'Erro ao gerar arquivo',
            401: 'Não autorizado'
        })
    def get(self):
        """Gera arquivo de retorno com as notas processadas"""
        pass

# Documentação Auth
@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.doc('login',
        description='Realiza autenticação do usuário',
        responses={
            200: 'Login realizado com sucesso',
            400: 'Dados inválidos',
            401: 'Credenciais inválidas'
        })
    @auth_ns.expect(login_model)
    def post(self):
        """Realiza login do usuário no sistema"""
        pass 