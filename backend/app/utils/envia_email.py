import boto3
import json
from flask import jsonify, current_app

def envia_email(destinatarios, assunto, corpo, anexos=None, configs=None):
    # Dicionário de dados a ser enviado
    data_to_send = {
        "destinatarios": destinatarios,
        "assunto": assunto,
        "corpo": corpo,
        "anexos": anexos,
        "configs": configs,
    }

    try:
        # Inicializa o cliente SQS
        sqs = boto3.client('sqs', region_name=current_app.config.get('AWS_REGION'))
        
        # URL da fila SQS - você precisará configurar isso no seu ambiente
        queue_url = current_app.config.get('AWS_SQS_QUEUE_URL_EMAIL')

        # Envia a mensagem para a fila SQS
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(data_to_send),
            MessageAttributes={
                'EmailType': {
                    'DataType': 'String',
                    'StringValue': 'standard'
                }
            }
        )

        current_app.logger.info(f"Mensagem enviada para SQS com MessageId [backend/utils/envia_email]: {response['MessageId']}")

        return jsonify({
            "message": "Email enviado para processamento",
            "messageId": response['MessageId'],
            "queueUrl": queue_url
        }), 202  # 202 Accepted indica que a requisição foi aceita para processamento

    except Exception as e:
        current_app.logger.error(f"Erro ao enviar mensagem para SQS: {e}")
        return jsonify({"erro": str(e)}), 500


# import boto3
# import json
# from flask import jsonify, current_app


# def envia_email(destinatarios, assunto, corpo, anexos=None, configs=None):
#     # Dicionário de dados a ser enviado
#     data_to_send = {
#         "destinatarios": destinatarios,
#         "assunto": assunto,
#         "corpo": corpo,
#         "anexos": anexos,
#         "configs": configs,
#     }

#     try:
#         # Inicializa o cliente Lambda
#         client = boto3.client("lambda")

#         # TODO: Fazer isso funciona no ambiente local
#         # Invoca a função Lambda
#         response = client.invoke(
#             FunctionName="aeco-enviador-email-lambda",
#             InvocationType="RequestResponse",
#             Payload=json.dumps(data_to_send),
#         )

#         # Lê a resposta da Lambda
#         response_payload = json.loads(response["Payload"].read())
#         current_app.logger.info(f"Resposta da invocação da Lambda: {response_payload}")

#         return jsonify(response_payload), 200  # Retorna a resposta da Lambda
#     except Exception as e:
#         current_app.logger.info(f"Falhou invocando a Lambda: {e}")
#         return jsonify({"erro": str(e)}), 500
