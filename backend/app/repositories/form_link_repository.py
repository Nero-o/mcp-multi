from flask import current_app
from app.models.form_link_model import FormLink
from app.extensions.database import db

class FormLinkRepository:
    @staticmethod
    def create_form_link(data):
        try:
            form_link = FormLink(**data)
            db.session.add(form_link)
            db.session.commit()
            return form_link
        except Exception as e:
            current_app.logger.error(f"Error creating form link: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_form_link_by_id(link_id):
        return FormLink.query.filter_by(link_id=link_id).first()
    
    @staticmethod
    def get_form_links_by_parceiro(parceiro_id):
        return FormLink.query.filter_by(parceiro_id=parceiro_id, is_active=True).all()
    
    @staticmethod
    def deactivate_link(link_id):
        form_link = FormLink.query.filter_by(link_id=link_id).first()
        if form_link:
            form_link.is_active = False
            db.session.commit()
            return True
        return False