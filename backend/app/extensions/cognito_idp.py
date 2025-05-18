import boto3
from flask import current_app
from app.utils.hash import calculate_secret_hash_cognito

class CognitoIDP():

    def __init__(self, cognito):
        # Inicializar o cliente boto3 para ações administrativas
        self.cognito = cognito
        self.client = boto3.client('cognito-idp', region_name=self.cognito.region)
        
    
    def get_user_group(self, user):
        response = self.client.admin_list_groups_for_user(
            Username=user,
            UserPoolId=self.cognito.user_pool_id,
        )
        return response
    
    def get_user(self, username):
        response = self.client.admin_get_user(
            UserPoolId=self.cognito.user_pool_id,
            Username=username
        )
        return response
    
    def read_id_token(self, id_token):
        token_info = {
            'email': id_token['email'],
            'username': id_token['sub'],
            'role': id_token['cognito:groups']
        }
        return token_info

    def get_secret_hash(self, email):
        try:
            secret_hash = calculate_secret_hash_cognito(
                client_id=self.cognito.client_id,
                client_secret=self.cognito.client_secret,
                username=email
            )
        except Exception as e:
            current_app.logger.error(f"Erro: {e}")
            return False

        return secret_hash
    
    def get_all_user(self, limit=50):
        users = []
        try:
            response = self.client.list_users(
                UserPoolId=self.cognito.user_pool_id,
                Limit=limit  # Define o número de usuários retornados por página
            )
            users.extend(response.get('Users', []))

            # Paginação caso haja mais usuários
            while 'PaginationToken' in response:
                response = self.client.list_users(
                    UserPoolId=self.cognito.user_pool_id,
                    Limit=limit,
                    PaginationToken=response['PaginationToken']
                )
                users.extend(response.get('Users', []))

        except Exception as e:
            current_app.logger.error(f"Erro ao listar usuários: {str(e)}")

        return users
    
    def translate_user_from_cognito(self, user):
        username = user['Username']
        
        col_cognito = 'Attributes' if 'Attributes' in user else 'UserAttributes'

        attributes = {attr['Name']: attr['Value'] for attr in user[col_cognito]}
        
        email = attributes.get('email', '')
        tenant_user = attributes.get('custom:tenant', '')
    
        # Obtenha os grupos do usuário
        group_response = self.get_user_group(username)
        groups = group_response.get('Groups', [])
        group_names = [group['GroupName'] for group in groups]
        role = group_names[0] if group_names else ''

        # Monte o dicionário conforme o formato desejado
        user_info = {
            'email': email,
            'username': username,
            'role': role,
            'tenant': tenant_user
        }
        
        return user_info
    

    def reset_password_with_code(self, email, code, senha):
        response = self.client.confirm_forgot_password(
            ClientId=self.cognito.client_id,
            Username=email,
            ConfirmationCode=code,
            Password=senha,
            SecretHash=self.get_secret_hash(email)
        )
        return response
    
    def esqueci_senha(self, email):
        try:
            self.client.forgot_password(
                ClientId=self.cognito.client_id,
                Username=email,
                SecretHash=self.get_secret_hash(email)
            )
        except Exception as e:
            current_app.logger.error(f"Erro ao enviar código de verificação: {e}")
            return {"error": "Usuário inválido"}, 401
        
        return {"msg": "Código de verificação enviado para o email"}

            
    def respond_to_new_password_challenge(self, email, new_password, session):
        try:
            secret_hash = self.get_secret_hash(email)
            response = self.client.respond_to_auth_challenge(
                ClientId=self.cognito.client_id,
                ChallengeName='NEW_PASSWORD_REQUIRED',
                Session=session,
                ChallengeResponses={
                    'USERNAME': email,
                    'NEW_PASSWORD': new_password,
                    'SECRET_HASH': secret_hash
                }
            )
            return response  # Sempre retorna um dicionário
        except self.client.exceptions.InvalidPasswordException as e:
            current_app.logger.error(f"Senha inválida: {e}")
            return {"error": "A nova senha não atende aos requisitos de segurança."}
        except self.client.exceptions.NotAuthorizedException as e:
            current_app.logger.error(f"Não autorizado: {e}")
            return {"error": "Usuário não autorizado."}
        except Exception as e:
            current_app.logger.error(f"Erro ao responder ao desafio de nova senha: {e}")
            return {"error": "Erro ao alterar a senha. Por favor, tente novamente mais tarde."}


    def authenticate_user(self, email, password):
        try:
            secret_hash = self.get_secret_hash(email)
            # Iniciar o processo de autenticação com email e senha
            response = self.client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password,
                    'SECRET_HASH': secret_hash
                },
                ClientId=self.cognito.client_id
            )

            # Verifica se um desafio foi retornado
            if 'ChallengeName' in response and response['ChallengeName'] == 'NEW_PASSWORD_REQUIRED':
                return {
                    'ChallengeName': response['ChallengeName'],
                    'Session': response['Session'],
                    'msg': 'É necessário alterar a senha temporária.'
                }, 200

            return response  # Contém tokens de acesso, ID e refresh
        except self.client.exceptions.NotAuthorizedException as e:
            current_app.logger.error(f"Usuário não autorizado. {e}")
            return {"error": "Usuário ou senha inválidos"}, 401
        except self.client.exceptions.UserNotConfirmedException as e:
            current_app.logger.error(f"Usuário não confirmado. {e}")
            return {"error": "Usuário ou senha inválidos"}
        except self.client.exceptions.UserNotFoundException as e:
            current_app.logger.error(f"Usuário não encontrado. {e}")
            return {"error": "Usuário ou senha inválidos"}, 401
        except Exception as e:
            current_app.logger.error(f"Erro na autenticação: {e}")
            return {"error": "Usuário ou senha inválidos"}, 401
