import os
import jwt # type: ignore
from flask import jsonify, g, current_app  # type: ignore

class CognitoService:

    @staticmethod
    def alterar_senha_usuario(senha_atual, nova_senha, client, access_token):
        try:
            response = client.change_password(
                PreviousPassword=senha_atual,
                ProposedPassword=nova_senha,
                AccessToken=access_token
            )
            return response
        except client.exceptions.NotAuthorizedException:
            return {"error": "Senha atual incorreta."}
        except client.exceptions.InvalidPasswordException as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": "Erro ao alterar a senha: {}".format(str(e))}


    @staticmethod
    def auth_user(username, senha):
        response = g.cognito_idp.authenticate_user(username, senha)

        if 'error' in response:
            return jsonify(response), 401
        
        if isinstance(response, tuple):
            # Verifica se é um desafio de nova senha
            if response[0].get('ChallengeName') == 'NEW_PASSWORD_REQUIRED':

                return jsonify({
                    'ChallengeName': 'NEW_PASSWORD_REQUIRED',
                    'Session': response[0]['Session'],
                    'msg': response[0]['msg']
                }), 200
            else:
                # Retorna erro (ex: 401, 404)
                return jsonify(response[0]), response[1]
        
        # Continua com o fluxo normal de login
        access_token = response['AuthenticationResult']['AccessToken']
        id_token = response['AuthenticationResult']['IdToken']
        refresh_token = response['AuthenticationResult']['RefreshToken']
        id_token_info = jwt.decode(id_token, options={"verify_signature": False})
    
        user_data = g.cognito_idp.read_id_token(id_token_info)

        return {
            'user_data' : user_data,
            'access_token' : access_token,
            'id_token' : id_token,
            "refresh_token": refresh_token  
        }
    
    @staticmethod
    def get_user_cognito(username):
        usuario_cognito_exists = g.cognito_idp.get_user(username)

        if usuario_cognito_exists:
            return usuario_cognito_exists
        else:
            return False
        

    @staticmethod
    def update_email_verified(email):
        user_pool_id = os.getenv('USER_POOL_ID')
        try:
            response = g.cognito_idp.client.admin_update_user_attributes(
                UserPoolId=user_pool_id,
                Username=email,
                UserAttributes=[
                    {
                        'Name': 'email_verified',
                        'Value': 'true'
                    }
                ]
            )
            return response
        except Exception as e:
            # Log the exception as needed
            return {'error': str(e)}
        

    @staticmethod
    def new_password_challenge(email, password, session):
        response = g.cognito_idp.respond_to_new_password_challenge(email, password, session)
        return response
    
    
    @staticmethod
    def read_id_token(id_token):
        response = g.cognito_idp.read_id_token(id_token)
        return response


    @staticmethod  
    def reset_password_with_code(email, code, password):
        response = g.cognito_idp.reset_password_with_code(email, code, password)
        return response
    

    @staticmethod  
    def forgot_password(email):
        response = g.cognito_idp.esqueci_senha(email)
        return response
    

    @staticmethod
    def get_user_by_email(email):
        if not email or not isinstance(email, str):
            raise ValueError("Email inválido")
        
        try:
            response = g.cognito_idp.client.list_users(
                UserPoolId=g.cognito.user_pool_id,
                Filter=f'email = "{email}"',
                Limit=1
            )
            users = response.get("Users", [])
            return users[0] if users else None
        except Exception as e:
            current_app.logger.error(f"Erro ao buscar usuário: {e}")
            return None

    

    @staticmethod
    def admin_create_user(username, lista_atributos, envia_email=False, senha_temporaria=None):
        try:
            params = {
                'UserPoolId': g.cognito.user_pool_id,
                'Username': username,
                'UserAttributes': lista_atributos
            }
            
            if not envia_email:
                params['MessageAction'] = 'SUPPRESS'
            
            if senha_temporaria:
                params['TemporaryPassword'] = senha_temporaria

            response = g.cognito_idp.client.admin_create_user(**params)
            return response
        except g.cognito_idp.client.exceptions.UsernameExistsException:
            return CognitoService.get_user_by_email(username)
        except Exception as e:
            raise ValueError(f"Erro ao criar usuário: {e}")

    
    @staticmethod
    def admin_add_user_to_group(username, role):
        response = g.cognito_idp.client.admin_add_user_to_group(
            UserPoolId=g.cognito.user_pool_id,
            Username=username,
            GroupName=role
        )
        return response

    @staticmethod  
    def delete_user(username):
        response = g.cognito_idp.client.admin_delete_user(
            UserPoolId=g.cognito.user_pool_id,
            Username=username
        )
        return response
