# app/routes/form_webhook_route.py
from flask import Blueprint, request, jsonify, current_app
from app.services.form_link_service import FormLinkService
from app.services.fornecedor_service import FornecedorService
from app.services.parceiro_service import ParceiroService
from app.services.fornecedor_parceiro_service import FornecedorParceiroService
import logging

# Configure logger
logger = logging.getLogger('form_webhook_route')

form_webhook_bp = Blueprint("form_webhook", __name__)

@form_webhook_bp.route('/submit/<tenant_code>/<link_id>', methods=['POST'])
def form_submission(tenant_code, link_id):
    """Public endpoint to receive form submissions from external React form"""
    logger.info(f"Form submission received for tenant {tenant_code} with link {link_id}")
    
    try:
        # Validate the link
        validation = FormLinkService.validate_form_link(link_id, tenant_code)
        if not validation or not validation.get('valid'):
            logger.warning(f"Invalid form link: {link_id} for tenant {tenant_code}")
            return jsonify({"status": "error", "message": "Invalid or expired form link"}), 400
        
        # Extract form data
        data = request.get_json()
        logger.info(f"Form data received: {data}")
        
        # Check mandatory fields
        required_fields = ['nome', 'email', 'cpf_cnpj']
        for field in required_fields:
            if field not in data or not data[field]:
                logger.warning(f"Missing required field: {field}")
                return jsonify({"status": "error", "message": f"Missing required field: {field}"}), 400
        
        # Get the parceiro
        parceiro_id = validation.get('parceiro_id')
        parceiro = ParceiroService.get_parceiro_por_id(parceiro_id)
        if not parceiro:
            logger.error(f"Parceiro not found for ID: {parceiro_id}")
            return jsonify({"status": "error", "message": "Partner not found"}), 400
        
        # Process fornecedor data
        fornecedor_data = {
            'nome': data.get('nome'),
            'email': data.get('email'),
            'cpf_cnpj': data.get('cpf_cnpj'),
            'telefone': data.get('telefone'),
            'endereco': data.get('endereco'),
            'cidade': data.get('cidade'),
            'estado': data.get('estado'),
            'cep': data.get('cep'),
            'contato_nome': data.get('contato_nome'),
            'contato_email': data.get('contato_email'),
            'contato_telefone': data.get('contato_telefone')
        }
        
        # Check if fornecedor already exists
        existing_fornecedor = FornecedorService.get_fornecedor_por_cpf_cnpj(fornecedor_data['cpf_cnpj'])
        
        if existing_fornecedor:
            fornecedor_id = existing_fornecedor.id
            # Update with new info
            FornecedorService.update_fornecedor(fornecedor_id, fornecedor_data)
            logger.info(f"Updated existing fornecedor: {fornecedor_id}")
        else:
            # Create new fornecedor
            new_fornecedor = FornecedorService.create_fornecedor(fornecedor_data)
            if not new_fornecedor:
                logger.error("Failed to create fornecedor")
                return jsonify({"status": "error", "message": "Failed to create supplier"}), 500
            fornecedor_id = new_fornecedor.id
            logger.info(f"Created new fornecedor: {fornecedor_id}")
        
        # Associate fornecedor with parceiro if not already associated
        fornecedor_parceiro = FornecedorParceiroService.get_by_fornecedor_parceiro(
            fornecedor_id=fornecedor_id, 
            parceiro_id=parceiro_id
        )
        
        if not fornecedor_parceiro:
            # Create association
            association_data = {
                'fornecedor_id': fornecedor_id,
                'parceiro_id': parceiro_id
            }
            
            # Add optional rate fields if present in form data
            rate_fields = ['taxa_tac_lote', 'taxa_tac_individual', 
                         'taxa_desconto_lote', 'taxa_desconto_individual']
            
            for field in rate_fields:
                if field in data and data[field] is not None:
                    association_data[field] = data[field]
            
            FornecedorParceiroService.create_fornecedor_parceiro(association_data)
            logger.info(f"Created association between fornecedor {fornecedor_id} and parceiro {parceiro_id}")
        
        return jsonify({
            "status": "success", 
            "message": "Form submitted successfully",
            "fornecedor_id": fornecedor_id,
            "parceiro_id": parceiro_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error processing form submission: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500