from flask import Blueprint, request, jsonify, url_for, redirect
import xml.etree.ElementTree as ET
from services.docusign_service import DocuSignService
from utils.logger import logger

docusign_bp = Blueprint('docusign', __name__)
docusign_service = DocuSignService()

# Endpoint para receber callbacks do DocuSign
@docusign_bp.route('/docusign/callback', methods=['GET'])
def docusign_callback():
    try:
        data = request.args
        envelope_id = data.get('envelope_id')
        signer_type = data.get('signer_type')
        event_type = data.get('event')
        
        logger.info(f"Callback recebido: Envelope ID: {envelope_id}, Signer Type: {signer_type}, Event: {event_type}")

        # Se for cedente que acabou de assinar, tentamos enviar email para o sacado
        if signer_type == 'cedente':
            try:
                result = docusign_service.enviar_url_assinatura_sacado(envelope_id)
                logger.info(f"Resultado do processamento para sacado: {result}")
            except Exception as e:
                logger.error(f"Erro ao processar assinatura para sacado: {str(e)}")

        if event_type == 'signing_complete':
            return redirect(url_for('assinatura_sucesso'))
        else:
            return redirect(url_for('assinatura_erro'))

    except Exception as e:
        logger.error(f"Erro no callback: {str(e)}")
        return redirect(url_for('assinatura_erro'))

@docusign_bp.route('/docusign-webhook', methods=['POST', 'GET'])
def docusign_webhook():
    logger.info("Recebendo webhook do DocuSign")
    try:
        # Parse do XML recebido
        xml_data = request.data
        root = ET.fromstring(xml_data)
        
        # Define o namespace para buscar elementos
        namespace = {'docusign': 'http://www.docusign.net/API/3.0'}
        
        # Obtém o EnvelopeStatus
        envelope_status = root.find('.//docusign:EnvelopeStatus', namespace)
        envelope_id = envelope_status.find('.//docusign:EnvelopeID', namespace).text
        
        # Busca os RecipientStatuses
        recipient_statuses = envelope_status.find('.//docusign:RecipientStatuses', namespace)
        
        # Verifica o status de cada recipient
        cedente_signed = False
        sacado_signed = False
        
        for recipient in recipient_statuses.findall('.//docusign:RecipientStatus', namespace):
            routing_order = recipient.find('.//docusign:RoutingOrder', namespace).text
            status = recipient.find('.//docusign:Status', namespace).text
            
            logger.info(f"Recipient - Routing Order: {routing_order}, Status: {status}")
            
            if routing_order == '1':  # Cedente
                cedente_signed = (status == 'Completed')
            elif routing_order == '2':  # Sacado
                sacado_signed = (status == 'Completed')
        
        # Verifica se ambos assinaram
        if cedente_signed and sacado_signed:
            logger.info(f"Ambos os signatários assinaram o envelope {envelope_id}. Enviando email de notificação...")
            # Adicionar código para notificar administrador ou atualizar status
            
        # Se o cedente assinou e o sacado está pendente
        elif cedente_signed and not sacado_signed:
            logger.info(f"Cedente assinou o envelope {envelope_id}. Notificando sacado...")
            
            # Busca a nota e envia email para o sacado
            try:
                nota = docusign_service._obter_nota_por_envelope_id(envelope_id)
                if nota:
                    url_assinatura = docusign_service.get_sacado_signing_url(envelope_id, nota)
                    docusign_service._enviar_email_sacado(nota, url_assinatura)
                    logger.info(f"Email enviado para sacado: {nota.email_sacado}")
                else:
                    logger.error(f"Nota não encontrada para o envelope {envelope_id}")
            except Exception as e:
                logger.error(f"Erro ao notificar sacado: {str(e)}")

        return jsonify({'status': 'success', 'envelope_id': envelope_id}), 200
        
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

@docusign_bp.route('/assinatura/sucesso')
def assinatura_sucesso():
    return "Assinatura realizada com sucesso", 200

@docusign_bp.route('/assinatura/erro')
def assinatura_erro():
    return "Erro ao realizar a assinatura", 400