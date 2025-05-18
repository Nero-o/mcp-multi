import boto3

class CognitoIdentity():
    def __init__(self, cognito):
        # Inicializar o cliente boto3 para ações administrativas
        self.cognito = cognito
        self.cognito_client_identity = boto3.client('cognito-identity', region_name=self.cognito.region)
    
