from flask import Blueprint, request, jsonify, g, current_app
from app.services.form_link_service import FormLinkService

form_link_bp = Blueprint("form_link", __name__)

@form_link_bp.route('/generate_form_link', methods=['POST'])
def generate_form_link():
    """Generate a new form link for a tenant"""
    try:
        data = request.get_json()
        parceiro_id = data.get('parceiro_id')
        description = data.get('description')
        days_valid = data.get('days_valid', 30)
        
        if not parceiro_id:
            return {"error": "Partner ID is required"}, 400
            
        result = FormLinkService.generate_form_link(
            parceiro_id=parceiro_id, 
            description=description,
            days_valid=days_valid
        )
        
        if not result:
            return {"error": "Could not generate form link"}, 400
            
        return result, 201
    except Exception as e:
        current_app.logger.error(f"Error generating form link: {str(e)}")
        return {"error": str(e)}, 500

@form_link_bp.route('/form_links', methods=['GET'])
def get_form_links():
    """Get all form links for a tenant"""
    try:
        parceiro_id = request.args.get('parceiro_id')
        if not parceiro_id:
            return {"error": "Partner ID is required"}, 400
            
        links = FormLinkService.get_links_by_parceiro(parceiro_id)
        
        result = []
        for link in links:
            base_url = request.host_url.rstrip('/')
            full_url = f"{base_url}/api/form/{link.parceiro.tenant_code}/{link.link_id}"
            
            result.append({
                'id': link.id,
                'link_id': link.link_id,
                'url': full_url,
                'description': link.description,
                'expiry_date': link.expiry_date,
                'is_active': link.is_active,
                'parceiro_id': link.parceiro_id,
                'tenant_code': link.parceiro.tenant_code
            })
            
        return {"links": result}, 200
    except Exception as e:
        current_app.logger.error(f"Error fetching form links: {str(e)}")
        return {"error": str(e)}, 500

@form_link_bp.route('/deactivate_form_link/<link_id>', methods=['POST'])
def deactivate_form_link(link_id):
    """Deactivate a form link"""
    try:
        result = FormLinkService.deactivate_link(link_id)
        if not result:
            return {"error": "Link not found or already deactivated"}, 404
            
        return {"message": "Link successfully deactivated"}, 200
    except Exception as e:
        current_app.logger.error(f"Error deactivating form link: {str(e)}")
        return {"error": str(e)}, 500