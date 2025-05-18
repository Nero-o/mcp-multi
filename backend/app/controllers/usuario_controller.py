from app.services.usuario_service import UsuarioService
from app.services.parceiro_service import ParceiroService
from flask import jsonify, g, current_app
from app.utils.paginacao import PaginacaoHelper
from app.utils.serializer import Serializer
from app.utils.senha_temporaria import gerar_senha_temporaria
from app.services.cognito_service import CognitoService
from app.services.redis_service import RedisService

class UsuarioController:
    ROLES_PERMITIDOS = ['Fornecedor', 'Parceiro', 'ParceiroAdministrador', 'Administrador']
    
    @staticmethod
    def get_user_db_logado(request, usuario_logado, tenant_url):
        parceiro = ParceiroService.get_parceiro_por_tenant(tenant_url)
        parceiro_id = parceiro.id

        if usuario_logado['role'] == 'Fornecedor' or usuario_logado['role'][0] == 'Fornecedor':
            usuario_role = 'Fornecedor'
        elif usuario_logado['role'] == 'Parceiro' or usuario_logado['role'][0] == 'Parceiro' or usuario_logado['role'] == 'ParceiroAdministrador' or usuario_logado['role'][0] == 'ParceiroAdministrador':
            usuario_role = 'Parceiro'
        elif usuario_logado['role'] == 'Administrador' or usuario_logado['role'][0] == 'Administrador':
            usuario_role = 'Administrador'
        else:
            return jsonify({"error": "Acesso negado."}), 401
        

        if usuario_role == 'Administrador':
            usuario = UsuarioService.get_usuario_por_username(usuario_logado['username'], parceiro_id)[0]

        if usuario_role == 'Parceiro':
            usuario = UsuarioService.get_usuario_por_username(usuario_logado['username'], parceiro_id)[0]

        if usuario_role == 'Fornecedor':
            session_id = request.cookies.get('session_id')
            
            if not session_id:
                return jsonify({"error": "Nenhum session_id enviado"}), 400
            
            session_data = RedisService.get_session(session_id)
            
            if not session_data:
                return jsonify({'error': 'Dados da sessão não encontrados.'}), 401
            
            if not session_data['user']['fornecedor_selected']:
                return jsonify({'error': 'Fornecedor não selecionado.'}), 401
            
            fornecedor_id = session_data['user']['fornecedor_selected']['id']

            usuario = UsuarioService.get_usuario_por_fornecedor_parceiro(fornecedor_id, parceiro_id)

        return usuario

    @staticmethod    
    def get_all_usuario(page, per_page):
        query = UsuarioService.get_all_usuario()
        return PaginacaoHelper.paginate_query(
            query,
            page,
            per_page,
            serialize_func=Serializer.serialize_usuario
        )
    
    @staticmethod
    def get_usuario_por_fornecedor_parceiro(fornecedor_id, parceiro_id):
        return UsuarioService.get_usuario_por_fornecedor_parceiro(fornecedor_id=fornecedor_id, parceiro_id=parceiro_id)


    @staticmethod
    def valida_vinculo_usuario_parceiro_logado(usuario_logado, tenant_code_url, retorna_lista_usuarios=None): 
        if not usuario_logado or 'username' not in usuario_logado or 'ip' not in usuario_logado:
            return False, "Usuário ou tenant inválido. 1.1"
        
        usuarios_do_email_logado = UsuarioService.get_usuario_por_username(usuario_logado['username'])

        if not usuarios_do_email_logado:
            return False, "Usuário ou tenant inválido. 2.2"
                        
        parceiro_da_url = ParceiroService.get_parceiro_por_tenant(tenant_code_url)

        if not parceiro_da_url:
            return False, "Usuário ou tenant inválido. 3.3"
        
        # Verifica se o usuário tem algum vínculo com o parceiro, e, se tiver,
        # monta uma lista com todos usuarios, deste email, vinculados ao parceiro
        usuarios_validos = [
            usuario for usuario in usuarios_do_email_logado
            if usuario.parceiro_id == parceiro_da_url.id
        ]
        
        if not usuarios_validos:
            return False, "Usuário ou tenant inválido. 4.4"

        if retorna_lista_usuarios:
            return usuarios_validos, "Usuário autenticado. 1.1"

        usuario = usuarios_validos[0]
        return usuario, "Usuário autenticado com sucesso. 1.1"
    

    @staticmethod
    def get_usuario_por_id(usuario_id):
        return UsuarioService.get_usuario_por_id(usuario_id)
    
    @staticmethod
    def get_usuario_por_username(username):
        return UsuarioService.get_usuario_por_username(username)
    
    # UPDATE
    @staticmethod
    def update_usuario(usuario_id, dados):
        return UsuarioService.update_usuario(usuario_id, dados)

    @staticmethod
    def update_usuario_por_idp_user_id(idpUserId,dados):
        return UsuarioService.update_usuario_por_idp_user_id(idpUserId, dados)
    
    @staticmethod
    def delete_usuario(usuario_id):
        return UsuarioService.delete_usuario(usuario_id)

    @staticmethod
    def create_usuario(dados):
        """
        Controller para criação de usuário com todas as validações necessárias.
        """
        try:
            # Validação básica dos campos obrigatórios
            if not UsuarioController._validar_campos_obrigatorios(dados):
                return jsonify({
                    'error': 'Campos obrigatórios não informados: email, role'
                }), 400

            # Validação do role
            if not UsuarioController._validar_role(dados.get('role')):
                return jsonify({
                    'error': f'Role inválido. Valores permitidos: {", ".join(UsuarioController.ROLES_PERMITIDOS)}'
                }), 400

            # Validação específica para fornecedor
            if dados.get('role') == 'Fornecedor':
                validacao_fornecedor = UsuarioController._validar_campos_fornecedor(dados)
                if validacao_fornecedor:
                    return validacao_fornecedor

            # Validação de email
            if not UsuarioController._validar_email(dados.get('email')):
                return jsonify({
                    'error': 'Email inválido'
                }), 400

            # Prepara os dados para criação
            dados_processados = UsuarioController._preparar_dados_criacao(dados)

            # Chama o service para criar o usuário
            resultado = UsuarioService.create_usuario(dados_processados)
            
            if isinstance(resultado, tuple):
                return jsonify({'error': resultado[0]}), 400
                
            return jsonify({
                'data': resultado.serialize(),
                'message': 'Usuário criado com sucesso'
            }), 201

        except Exception as e:
            current_app.logger.error(f"Erro ao criar usuário: {str(e)}")
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def _validar_campos_obrigatorios(dados):
        """Valida se os campos obrigatórios estão presentes"""
        return all(campo in dados for campo in ['email', 'role'])

    @staticmethod
    def _validar_role(role):
        """Valida se o role é permitido"""
        return role in UsuarioController.ROLES_PERMITIDOS

    @staticmethod
    def _validar_campos_fornecedor(dados):
        """Valida campos obrigatórios para fornecedor"""
        campos_fornecedor = ['cpf_cnpj', 'razao_social']
        for campo in campos_fornecedor:
            if campo not in dados:
                return jsonify({
                    'error': f'Campo obrigatório para fornecedor não informado: {campo}'
                }), 400
        return None

    @staticmethod
    def _validar_email(email):
        """Valida formato básico do email"""
        return isinstance(email, str) and '@' in email

    @staticmethod
    def _preparar_dados_criacao(dados):
        """Prepara os dados para criação do usuário"""

        if not 'tenant_code' in dados:
            parceiro = ParceiroService.get_parceiro_por_tenant(g.tenant_url)
            dados.update({
                'parceiro_id': parceiro.id
            })
        else:
            dados['parceiro_id'] = dados['tenant_code']

        dados_criacao = {
            'username': dados['email'],
            'email': dados['email'],
            'role': dados['role'],
            'parceiro_id': dados['parceiro_id']
        }

        # Adiciona campos opcionais se existirem
        campos_opcionais = ['nome', 'telefone']
        for campo in campos_opcionais:
            if campo in dados:
                dados_criacao[campo] = dados[campo]

        # Adiciona campos do fornecedor se for o caso
        if dados['role'] == 'Fornecedor':
            campos_fornecedor = [
                'cpf_cnpj', 'razao_social', 'bco', 'agencia', 'conta',
                'municipio', 'uf', 'numero', 'complemento', 'bairro', 'cep'
            ]
            for campo in campos_fornecedor:
                if campo in dados:
                    dados_criacao[campo] = dados[campo]

        return dados_criacao