from flask import Blueprint, g, current_app
from app.services.parceiro_service import ParceiroService

tenant_bp = Blueprint("tenants", __name__)

@tenant_bp.route('/get-tenant', methods=['GET', 'POST'])
def get_tenant_url():
    # Pegando o host (incluindo o subdomínio)
    if hasattr(g, 'tenant_url'):
        tenant = g.tenant_url
        
    if not tenant:
        return {"msg": "Requisição inválida 1"}, 404
    
    tenant_info = ParceiroService.get_parceiro_por_tenant(tenant)

    if not tenant_info:
        return {"msg": "Requisição inválida 2"}, 404
    
    tenant_public_info = {
        "nome": tenant_info.nome,
        "logo": tenant_info.logo,
    }

    return tenant_public_info, 200