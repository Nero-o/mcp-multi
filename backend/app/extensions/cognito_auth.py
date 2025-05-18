import os

class Cognito:
    def __init__(self, oauth):
        self.region = os.getenv('AWS_REGION')
        self.user_pool_id = os.getenv('USER_POOL_ID')
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')

        # Inicializar o cliente OAuth para fluxos de autenticação
        self.oauth_client = oauth.register(
            name='cognito',
            client_id=self.client_id,
            client_secret=self.client_secret,
            server_metadata_url=os.getenv('COGNITO_KEYS_URL'),  # URL de configuração OpenID Connect
            client_kwargs={"scope": "openid email"},
        )
