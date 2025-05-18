from app.extensions.database import db
from . import BaseModel
import uuid

class FormLink(BaseModel):
    __tablename__ = 'form_link'

    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.String(64), unique=True, default=lambda: str(uuid.uuid4()))
    is_active = db.Column(db.Boolean, default=True)
    description = db.Column(db.String(255), nullable=True)
    expiry_date = db.Column(db.DateTime, nullable=True)
    
    # Foreign keys
    parceiro_id = db.Column(
        db.Integer,
        db.ForeignKey('parceiro.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # Relationships
    parceiro = db.relationship(
        'Parceiro',
        backref=db.backref('form_links', cascade='all, delete-orphan')
    )