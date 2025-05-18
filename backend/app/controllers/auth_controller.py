import jwt
import uuid
from flask import current_app, jsonify, g, request
from app.services.cognito_service import CognitoService
from app.services.parceiro_service import ParceiroService 
from app.services.redis_service import RedisService
from app.controllers.usuario_controller import UsuarioController
from app.services.fornecedor_service import FornecedorService
from app.services.fornecedor_parceiro_service import FornecedorParceiroService
from app.services.config_tenant_service import ConfigTenantService

class AuthController:

    @staticmethod
    def select_fornecedor_login(session_id, selected_fornecedor_id, tenant):

        tenant = ParceiroService.get_parceiro_por_tenant(g.tenant_url)
        if not tenant:
            return jsonify({'error': 'Tenant inválido.'}), 401
 
        # Get the session data from Redis
        session_data = RedisService.get_session(session_id)
        if not session_data:
            return jsonify({'error': 'Dados da sessão não encontrados.'}), 401

        try:
            selected_fornecedor_id = int(selected_fornecedor_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'ID de fornecedor inválido.'}), 400
        
        # Check if the user is a 'Fornecedor' role
        if 'Fornecedor' not in session_data['user']['role']:
            return jsonify({'error': 'Usuário não é um fornecedor.'}), 403

        # Check if the selected fornecedor is in the user's fornecedores list
        fornecedores = session_data['user'].get('fornecedores', [])
        if not fornecedores:
            return jsonify({'error': 'Usuário não possui fornecedores vinculados.'}), 403

        # Find the selected fornecedor in the list
        fornecedor_selected = next(
            (fornecedor for fornecedor in fornecedores if fornecedor['id'] == selected_fornecedor_id),
            None
        )

        if not fornecedor_selected:
            return jsonify({'error': 'Fornecedor selecionado não está vinculado ao usuário.'}), 403

        # Update the session data with the selected fornecedor
        session_data['user']['fornecedor_selected'] = fornecedor_selected

        usuario_selected = UsuarioController.get_usuario_por_fornecedor_parceiro(fornecedor_selected['id'], tenant.id)
        if not usuario_selected:
            return jsonify({'error': 'Usuário selecionado não está vinculado ao fornecedor.'}), 403
            
        termo_assinado = usuario_selected.assinatura_termo_de_uso
        contrato_assinado = usuario_selected.assinatura_contrato
            
        session_data['user']['fornecedor_selected'].update({
            'termo_assinado': termo_assinado,
            'contrato_assinado': contrato_assinado
        })

        # Save the updated session data back to Redis
        RedisService.save_session(session_id, session_data, current_app.config['EXPIRATION_TIME_COOKIE'])

                # Cria a resposta HTTP
        response = jsonify({'msg': 'Fornecedor selecionado com sucesso.'}) 
        
        return response
    
    @staticmethod
    def create_session_data(user_data, access_token, id_token, refresh_token, tenant, response_message="Sucesso"):
        parceiro = ParceiroService.get_parceiro_por_tenant(tenant)

        if not parceiro:
            return jsonify({'error': 'Tenant inválido'}), 404

        usuarios = UsuarioController.get_usuario_por_username(user_data['username'])
        
        ## Verifica se o usuário tem vinculo com o parceiro ##   
        usuarios_vinculados_com_tenant = [usuario for usuario in usuarios if usuario.parceiro_id == parceiro.id]

        if not usuarios_vinculados_com_tenant:
            return jsonify({'error': 'Nenhum usuário válido para o tenant especificado'}), 403
    

        if isinstance(user_data['role'], list):
            role = user_data['role'][0]
        else:
            role = user_data['role']

        if role == 'Fornecedor':
            user_data['fornecedores'] = []

            for usuario in usuarios_vinculados_com_tenant:
                fornecedor = FornecedorService.get_fornecedor_por_id(usuario.fornecedor_id)
                fornecedor_parceiro = FornecedorParceiroService.get_fornecedor_parceiro(parceiro.id, fornecedor.id)

                if fornecedor_parceiro.excluido == 0: 
                    fornecedor_dict = {
                        'id': fornecedor.id,
                        'razao_social': fornecedor.razao_social,
                        'cpf_cnpj': fornecedor.cpf_cnpj,
                        'excluido': fornecedor.excluido
                    }
                    user_data['fornecedores'].append(fornecedor_dict)
                    
        if role == 'ParceiroAdministrador' or role == 'Parceiro':
            config = ConfigTenantService.get_config_by_parceiro_id(parceiro.id)
            
            user_data['config'] = [{
                "opera_sacado": config['opera_sacado'],
                "opera_cedente": config['opera_cedente']
            }]

        # Gera um session_id único
        session_id = str(uuid.uuid4())

        # Cria o session_data
        session_data = {
            "user": user_data,
            "access_token": access_token,
            "id_token": id_token,
            "refresh_token": refresh_token
        }

        # Salva a sessão do usuário no Redis
        RedisService.save_session(session_id, session_data, current_app.config['EXPIRATION_TIME_COOKIE'])

        # Cria a resposta HTTP
        response = jsonify({"msg": response_message})

        response.set_cookie(
            'session_id',
            session_id,
            httponly=True,
            samesite='Lax',
            max_age=current_app.config['EXPIRATION_TIME_COOKIE']
        )

        response.set_cookie(
            'role_user',
            role,
            httponly=True,
            samesite='Lax',
            max_age=current_app.config['EXPIRATION_TIME_COOKIE']
        )

        return response
    
    @staticmethod
    def create_challenge_session(username, obj_response):
        temp_session_id = str(uuid.uuid4())
        temp_session_data = {
            "email": username,
            "session": obj_response['Session']
        }

        RedisService.save_session(temp_session_id, temp_session_data, 60 * 30)

        response = jsonify({
            'ChallengeName': 'NEW_PASSWORD_REQUIRED',
            'Session': obj_response['Session'],
            'msg': 'É necessário alterar a senha temporária.'
        })
        response.set_cookie(
            'temp_session_id',
            temp_session_id,
            httponly=True,
            samesite='Lax',
            max_age=current_app.config['EXPIRATION_TIME_COOKIE']
        )

        return response, 200
    
    @staticmethod
    def auth_login(username, senha, tenant):
        response_auth = CognitoService.auth_user(username, senha)

        #se retornar challenge ou erro, gravar email do usuario numa sessao temporaria do redis,
        #retornar o cookie com o ID da sessão temporária e enviar mensagem de que é necessário alterar a senha
        if isinstance(response_auth, tuple):
            obj_response = response_auth[0].get_json()

            if 'ChallengeName' in obj_response and obj_response['ChallengeName'] == 'NEW_PASSWORD_REQUIRED':
                return AuthController.create_challenge_session(username, obj_response)
        
            return response_auth[0], response_auth[1]
        
        ## se nao retornou erro nem challenge, entao response_auth é um dicionario de informacoes ##
        user_data = response_auth['user_data']
        
        username = user_data.get('username')
        if not username:
            return jsonify({'error': 'Username não encontrado nos dados do usuário'}), 400

        # Usa o método create_session_data
        response = AuthController.create_session_data(
            user_data=user_data,
            access_token=response_auth['access_token'],
            id_token=response_auth['id_token'],
            refresh_token=response_auth['refresh_token'],
            tenant=tenant
        )

        return response

    @staticmethod
    def new_password_challenge(email, senha, session):
        response = CognitoService.new_password_challenge(email, senha, session)

        if 'AuthenticationResult' in response:
            access_token = response['AuthenticationResult']['AccessToken']
            id_token = response['AuthenticationResult']['IdToken']

            id_token_info = jwt.decode(id_token, options={"verify_signature": False})

            user_data = CognitoService.read_id_token(id_token_info)

            # Atualiza o email como verificado
            update_response = CognitoService.update_email_verified(email)
            
            if 'error' in update_response:
                return jsonify({"error": "Falha ao verificar o email do usuário."}), 500

            # Usa o método create_session_data
            response = AuthController.create_session_data(
                user_data=user_data,
                access_token=access_token,
                id_token=id_token,
                refresh_token=response['AuthenticationResult']['RefreshToken'],
                tenant=g.tenant_url,
                response_message="Senha alterada e login realizado com sucesso"
            )

            idpUserId = user_data['username']
            UsuarioController.update_usuario_por_idp_user_id(idpUserId, {'senha_temporaria': None})

            return response, 200

        return jsonify({"msg": "Alteração de senha falhou."}), 400
            

    
    @staticmethod
    def logout(session_id):

        RedisService.delete_session(session_id)

        # Criar resposta
        response = jsonify({'msg': 'Logout realizado com sucesso.'})

        # Remover o cookie do cliente
        response.set_cookie('session_id', '', expires=0)
        response.set_cookie('role_user', '', expires=0)

        return response
    

    @staticmethod   
    def reset_password_with_code(email, code, senha):
        response = CognitoService.reset_password_with_code(email, code, senha)
        return response
    
    @staticmethod
    def forgot_password(email):
        response = CognitoService.forgot_password(email)
        return response
    

    @staticmethod
    def alterar_senha_usuario(senha_atual, nova_senha):
        client = g.cognito_idp.client
        session_id = request.cookies.get('session_id')
        session_data = RedisService.get_session(session_id)
        
        access_token = session_data.get('access_token')
        
        response = CognitoService.alterar_senha_usuario(senha_atual, nova_senha, client, access_token)
        if response.get('error'):
            return jsonify({"error": response['error']}), 400

        return jsonify({"msg": "Senha alterada com sucesso."}), 200
