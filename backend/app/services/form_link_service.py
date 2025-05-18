from app.repositories.form_link_repository import FormLinkRepository
from app.repositories.parceiro_repository import ParceiroRepository
from datetime import datetime, timedelta
import os

class FormLinkService:
    @staticmethod
    def generate_form_link(parceiro_id, description=None, days_valid=30):
        # Converter parceiro_id para inteiro
        parceiro_id = int(parceiro_id)
        
        # Validate parceiro exists
        parceiro = ParceiroRepository.get_parceiro_por_id(parceiro_id)
        if not parceiro:
            return None
            
        # Set expiry date (if days_valid is provided)
        expiry_date = None
        if days_valid:
            expiry_date = datetime.utcnow() + timedelta(days=days_valid)
            
        # Create form link
        data = {
            'parceiro_id': parceiro_id,
            'description': description,
            'expiry_date': expiry_date,
            'is_active': True
        }
        
        form_link = FormLinkRepository.create_form_link(data)
        if not form_link:
            return None
            
        # Generate public URL
        base_url = os.getenv('FORM_URL', 'https://forms.example.com')
        full_url = f"{base_url}/fornecedor?tenant={parceiro.tenant_code}&link={form_link.link_id}"
        
        return {
            'id': form_link.id,
            'link_id': form_link.link_id,
            'url': full_url,
            'parceiro_id': parceiro_id,
            'tenant_code': parceiro.tenant_code,
            'expiry_date': expiry_date
        }
    
    @staticmethod
    def validate_form_link(link_id, tenant_code):
        form_link = FormLinkRepository.get_form_link_by_id(link_id)
        if not form_link:
            return False
            
        # Check if link is active
        if not form_link.is_active:
            return False
            
        # Check if link has expired
        if form_link.expiry_date and form_link.expiry_date < datetime.utcnow():
            return False
            
        # Check tenant association
        if form_link.parceiro.tenant_code != tenant_code:
            return False
            
        return {
            'valid': True,
            'parceiro_id': form_link.parceiro_id,
            'tenant_code': form_link.parceiro.tenant_code
        }
    
    @staticmethod
    def get_links_by_parceiro(parceiro_id):
        return FormLinkRepository.get_form_links_by_parceiro(parceiro_id)
        
    @staticmethod
    def deactivate_link(link_id):
        return FormLinkRepository.deactivate_link(link_id)