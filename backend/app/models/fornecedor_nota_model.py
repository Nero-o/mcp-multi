# app/models/fornecedor_nota_model.py
from app.extensions.database import db
from . import BaseModel
from datetime import datetime
from sqlalchemy.sql import text

class FornecedorNota(BaseModel):
    __tablename__ = 'fornecedor_nota'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    titulo = db.Column(db.String(255), nullable=True)
    documento = db.Column(db.String(255), nullable=True)
    sacado = db.Column(db.String(255), nullable=True)
    email_sacado = db.Column(db.String(255), nullable=True)
    cnpj_sacado = db.Column(db.String(20), nullable=True)
    tipo_doc = db.Column(db.String(100), nullable=True) 
    
    email_aviso_expiracao = db.Column(db.Boolean, default=False, nullable=False)
    email_disponivel = db.Column(db.Boolean, default=False, nullable=False)
    
    tipo_operacao = db.Column(db.String(50), nullable=False, default='parceiro_sacado', server_default="parceiro_sacado") 
    metodo_assinatura = db.Column(db.String(50), nullable=False, default='aeco', server_default="aeco")  # 'aeco', 'docusign', 'd4sign'
    
    docusign_envelope_id = db.Column(db.String(255), nullable=True)
    d4sign_document_uuid = db.Column(db.String(255), nullable=True)

    ajuste_aeco_validado = db.Column(db.Float, nullable=True)
    vlr_face = db.Column(db.Float, nullable=True)
    vlr_disp_antec = db.Column(db.Float, nullable=True)
    valor_liquido = db.Column(db.Float, nullable=True)
    valor_liquido_aeco = db.Column(db.Float, nullable=True)
    fator_desconto = db.Column(db.Float, nullable=True)
    desconto_juros = db.Column(db.Float, nullable=True)
    desconto_tac = db.Column(db.Float, nullable=True)
    desconto = db.Column(db.Float, nullable=True)
    desconto_juros_aeco = db.Column(db.Float, nullable=True)
    desconto_tac_aeco = db.Column(db.Float, nullable=True)
    desconto_banco_aeco = db.Column(db.Float, nullable=True)
    desconto_aeco = db.Column(db.Float, nullable=True)
    taxa_total_aeco = db.Column(db.Float, nullable=True)
    valor_receber_aeco = db.Column(db.Float, nullable=True)
    dt_emis = db.Column(db.Date, nullable=True)
    dt_fluxo = db.Column(db.Date, nullable=True)
    dt_inicio = db.Column(db.Date, nullable=True)
    dt_fim = db.Column(db.Date, nullable=True)
   
    data_conclusao = db.Column(db.DateTime, nullable=True)
    data_assinatura = db.Column(db.DateTime, nullable=True)
    data_cancelamento = db.Column(db.DateTime, nullable=True)

    status_id = db.Column(
        db.Integer,
        db.ForeignKey('status_nota.id', ondelete='NO ACTION', name='FK_fornecedor_nota_status_nota'),
        nullable=False,
        default=1
    )
    status_admin_id = db.Column(
        db.Integer,
        db.ForeignKey('status_nota_admin.id', ondelete='NO ACTION', name='FK_fornecedor_nota_status_nota_admin'),
        nullable=False,
        default=1
    )
    fornecedor_id = db.Column(
        db.Integer,
        db.ForeignKey('fornecedor.id', ondelete='SET NULL', name='FK_fornecedor_nota_fornecedor'),
        nullable=True
    )
    parceiro_id = db.Column(
        db.Integer,
        db.ForeignKey('parceiro.id', ondelete='CASCADE', name='FK_fornecedor_nota_parceiro'),
        nullable=False
    )
    

    fornecedor = db.relationship(
        'Fornecedor',
        back_populates='notas',
        lazy='joined'
    )
    # Relações utilizando backref
    parceiro = db.relationship(
        'Parceiro',
        backref=db.backref('notas', cascade='all, delete-orphan', lazy='dynamic')
    )
    status_nota = db.relationship(
        'StatusNota',
        backref=db.backref('notas', cascade='all, delete-orphan', lazy='dynamic')
    )
    status_nota_admin = db.relationship(
        'StatusNotaAdmin',
        backref=db.backref('notas', cascade='all, delete-orphan', lazy='dynamic')
    )

    assinatura_nota = db.relationship(
        'AssinaturaNota',
        uselist=False,
        back_populates='nota',
        cascade='all, delete-orphan'
    )

    __table_args__ = (
        db.UniqueConstraint('titulo', 'fornecedor_id', 'parceiro_id', name='uq_titulo_fornecedor_parceiro'),
    )