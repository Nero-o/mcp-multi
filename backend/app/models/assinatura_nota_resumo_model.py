from app.extensions.database import db
from . import BaseModel

class AssinaturaNotaResumo(BaseModel):
    __tablename__ = 'assinatura_nota_resumo'
    
    id = db.Column(db.String(64), primary_key=True)  # lote_id
    qtd_notas = db.Column(db.Integer, default=0)
    vlr_total_face = db.Column(db.Float, default=0)
    vlr_total_disp_antec = db.Column(db.Float, default=0)
    vlr_total_liquido = db.Column(db.Float, default=0)
    vlr_total_liquido_aeco = db.Column(db.Float, default=0)
    desconto_total = db.Column(db.Float, default=0)
    desconto_total_aeco = db.Column(db.Float, default=0)
    valor_total_receber_aeco = db.Column(db.Float, default=0)
    dt_primeira_assinatura = db.Column(db.DateTime)
    dt_ultima_assinatura = db.Column(db.DateTime)
    dt_primeiro_vcto = db.Column(db.DateTime)
    dt_ultimo_vcto = db.Column(db.DateTime)
    status_id = db.Column(db.Integer)
    status_admin_id = db.Column(db.Integer)
    fornecedor_id = db.Column(db.Integer)
    parceiro_id = db.Column(db.Integer)
    lote_id = db.Column(db.String(64))
