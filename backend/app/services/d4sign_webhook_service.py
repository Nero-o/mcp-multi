# backend/app/services/d4sign_webhook_service.py
import os
import logging
import requests
from datetime import datetime
from flask import g, current_app
from typing import Dict, Any

# Configuração do logger
logger = logging.getLogger('d4sign_webhook')

class D4SignWebhookService:
    """Serviço para gerenciar webhooks da D4Sign"""
    
    @staticmethod
    def _get_webhook_url_for_tenant(tenant_url=None) -> str:
        """
        Constrói a URL do webhook específica para o tenant.
        """
        # Se nenhum tenant for fornecido, usar o tenant atual da requisição
        if not tenant_url and hasattr(g, 'tenant_url'):
            tenant_url = g.tenant_url
        
        # Se ainda não tiver tenant_url, usar um valor padrão
        if not tenant_url:
            logger.warning("Nenhum tenant disponível para construir webhook_url")
            # Usar a URL de webhook padrão se configurada
            return os.getenv('D4SIGN_WEBHOOK_URL', '')
        
        # Base domain configurada no ambiente
        # Construir a URL completa do webhook
        webhook_url = f"https://{tenant_url}.aecoapp.br/api/webhook/d4sign"
        
        logger.info(f"URL de webhook gerada para tenant {tenant_url}: {webhook_url}")
        return webhook_url
    
    @staticmethod
    def register_webhook(document_uuid: str, tenant_url=None, api_url=None, headers=None) -> Dict:
        """
        Registra um webhook para o documento no D4Sign.
        
        Args:
            document_uuid: UUID do documento
            tenant_url: URL do tenant (opcional)
            api_url: URL base da API D4Sign (opcional)
            headers: Headers para requisição (opcional)
            
        Returns:
            Dict com resultado da operação
        """
        logger.info(f"Registrando webhook para o documento {document_uuid}")
        
        try:
            # Gerar a URL do webhook para o tenant
            webhook_url = D4SignWebhookService._get_webhook_url_for_tenant(tenant_url)
            
            if not webhook_url:
                logger.warning("URL de webhook não pôde ser gerada")
                return {
                    'status': 'webhook_not_registered',
                    'document_uuid': document_uuid,
                    'reason': 'No webhook URL could be generated'
                }
            
            # Se api_url não for fornecida, usar a variável de ambiente
            if not api_url:
                api_url = os.getenv('D4SIGN_API_URL', 'https://sandbox.d4sign.com.br/api/v1')
            
            # Se headers não for fornecido, criar com as credenciais das variáveis de ambiente
            if not headers:
                headers = {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'tokenAPI': os.getenv('D4SIGN_API_TOKEN'),
                    'cryptKey': os.getenv('D4SIGN_CRYPTO_KEY')
                }
            
            url = f"{api_url}/documents/{document_uuid}/webhooks"
            
            payload = {
                'url': webhook_url
            }
            
            logger.info(f"Configurando webhook para documento {document_uuid}: {webhook_url}")
            response = requests.post(url, headers=headers, json=payload)
            
            # Processar resposta
            if response.status_code >= 200 and response.status_code < 300:
                try:
                    result = response.json() if response.text.strip() else {"success": True}
                    logger.info(f"Webhook registrado com sucesso para o documento {document_uuid}")
                except Exception:
                    result = {"success": True, "raw_response": response.text}
                    logger.warning(f"Resposta não é JSON válido: {response.text[:100]}...")
            else:
                error_msg = f"Erro na configuração de webhook: {response.status_code} - {response.text[:200]}"
                logger.error(error_msg)
                return {
                    'status': 'webhook_error',
                    'document_uuid': document_uuid,
                    'webhook_url': webhook_url,
                    'error': error_msg
                }
            
            return {
                'status': 'webhook_registered',
                'document_uuid': document_uuid,
                'webhook_url': webhook_url,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Erro ao registrar webhook: {str(e)}")
            return {
                'status': 'webhook_exception',
                'document_uuid': document_uuid,
                'error': str(e)
            }
    
    @staticmethod
    def process_webhook(request_data: Dict[str, Any]) -> Dict:
        """
        Processa os dados recebidos de um webhook da D4Sign.
        Por enquanto, apenas registra os dados nos logs para análise.
        """
        # Obter informações principais do webhook
        document_uuid = request_data.get('uuid')
        type_post = request_data.get('type_post')
        message = request_data.get('message')
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Registrar o evento de forma detalhada
        logger.info(f"[{timestamp}] Webhook D4Sign recebido:")
        logger.info(f"  Document UUID: {document_uuid}")
        logger.info(f"  Tipo de evento: {type_post}")
        logger.info(f"  Mensagem: {message}")
        logger.info(f"  Dados completos: {request_data}")
        
        # Interpretar o tipo de evento (apenas para logs)
        event_description = "Evento desconhecido"
        if type_post == '1':
            event_description = "Documento finalizado"
        elif type_post == '2':
            event_description = "Documento cancelado"
        elif type_post == '3':
            event_description = "Email não entregue"
        elif type_post == '4':
            event_description = "Assinatura de signatário"
            
        logger.info(f"  Descrição do evento: {event_description}")
        
        # Apenas para feedback na resposta da API
        return {
            "processed": True,
            "document_uuid": document_uuid,
            "event_type": type_post,
            "description": event_description,
            "timestamp": timestamp
        }