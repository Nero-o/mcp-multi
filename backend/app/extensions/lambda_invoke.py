import boto3
import json
import uuid
import os
from app.config import Config

sqs_client = boto3.client('sqs',region_name=Config.AWS_REGION)

class MessageProcessor:
    def __init__(self):
        self.client = sqs_client
        self.queue_url = Config.AWS_SQS_QUEUE_URL_CRONJOB
        
    def _message_id(self, id=None):
        return id if id else str(uuid.uuid4())
    
    def _prepare_message(self, tipo_tarefa, agendamento_id, parceiro_id, parametros):
        return {
            "tipo_tarefa": tipo_tarefa,
            "agendamento_id": agendamento_id,
            "parceiro_id": parceiro_id,
            "parametros": parametros
        }
        
    def send_to_queue(self, tipo_tarefa, agendamento_id, parceiro_id, parametros):
        try:
            mensagem = self._prepare_message(
                tipo_tarefa=tipo_tarefa,
                agendamento_id=agendamento_id,
                parceiro_id=parceiro_id,
                parametros=parametros
            )

            response = self.client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(mensagem)
            )

            return response

        except Exception as e:
            raise Exception(f"Erro ao enviar mensagem para fila SQS: {str(e)}")