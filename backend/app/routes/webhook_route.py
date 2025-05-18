# backend/app/routes/webhook_route.py
from flask import Blueprint, request, jsonify
import logging
from app.services.d4sign_webhook_service import D4SignWebhookService

# Configuração do logger
logger = logging.getLogger('webhook_route')

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route('/d4sign', methods=['POST'])
def d4sign_webhook():
    """Endpoint para receber webhooks da D4Sign"""
    logger.info("Webhook da D4Sign recebido")
    
    try:
        # Log dos headers para debug
        logger.info(f"Headers recebidos: {dict(request.headers)}")
        
        # Identificar o tipo de conteúdo
        content_type = request.headers.get('Content-Type', '')
        logger.info(f"Content-Type: {content_type}")
        
        # Processar dados conforme o tipo de conteúdo
        if 'multipart/form-data' in content_type or 'application/x-www-form-urlencoded' in content_type:
            logger.info("Processando como form-data")
            data = dict(request.form)
            
            # Verificar se há arquivos
            if request.files:
                files = list(request.files.keys())
                logger.info(f"Arquivos recebidos: {files}")
        else:
            # Tentar processar como JSON
            logger.info("Processando como JSON")
            data = request.get_json(silent=True) or {}
            
            # Se falhar, tentar como form-data
            if not data and request.form:
                logger.info("Fallback para form-data")
                data = dict(request.form)
                
        # Log dos dados recebidos
        logger.info(f"Dados recebidos: {data}")
        
        # Processar o webhook
        if data:
            result = D4SignWebhookService.process_webhook(data)
            return jsonify({"status": "success", "message": "Webhook recebido e registrado", "data": result}), 200
        else:
            logger.warning("Nenhum dado válido encontrado no webhook")
            return jsonify({"status": "error", "message": "Nenhum dado válido encontrado"}), 400
            
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500