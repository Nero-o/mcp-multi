from app.extensions.database import db
from app.models.assinatura_nota_model import AssinaturaNota

class AssinaturaFornecedorNotaRepository:

    @staticmethod
    def get_assinatura_por_nota_e_usuario(nota_id, usuario_id):
        return AssinaturaNota.query.filter_by(nota_id=nota_id, usuario_id=usuario_id).first()
        
    @staticmethod
    def registrar_assinatura_nota(usuario_id, nota_id, dados_assinatura):
        assinatura_nota = AssinaturaNota(usuario_id=usuario_id, nota_id=nota_id, **dados_assinatura)
        db.session.add(assinatura_nota)
        db.session.commit()
        return assinatura_nota
