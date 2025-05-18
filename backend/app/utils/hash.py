import hmac
import hashlib
import base64
from datetime import datetime

def calculate_secret_hash_cognito(client_id, client_secret, username):
    message = username + client_id

    dig = hmac.new(
        str(client_secret).encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    
    return base64.b64encode(dig).decode()

def create_hash_assinatura(dados, tipo):
    now = datetime.now()
    timestamp = now.isoformat()

    hash_column = f'hash_{tipo}'
    data_assinatura_column = f'data_assinatura_{tipo}'
    
    if 'fornecedor_id' in dados:
        data_string = f"{dados['fornecedor_id']}|{timestamp}|assinou_{tipo}"
    elif 'usuario_id' in dados:
        data_string = f"{dados['usuario_id']}|{timestamp}|assinou_{tipo}"
    elif 'parceiro_id' in dados:
        data_string = f"{dados['parceiro_id']}|{timestamp}|assinou_{tipo}"
    else:
        data_string = f"{timestamp}|assinou_{tipo}"

    hash_object = hashlib.sha256(data_string.encode())
    hex_dig = hash_object.hexdigest()

    assinatura_string = f"Hash: {str(hex_dig)} - IP: {str(dados['ip'])} - Registrado em: {now.strftime('%d/%m/%Y %H:%M:%S')}"
    
    dados_assinatura = {
        hash_column: hex_dig,
        'ip':dados['ip'],
        'assinatura': assinatura_string,
        data_assinatura_column: now,
    }

    return dados_assinatura
