from app.extensions.database import db
from app.models.assinatura_upload import AssinaturaUpload

class AssinaturaUploadRepository:
    @staticmethod
    def registrar_assinatura_upload(dados_assinatura):
        assinatura = AssinaturaUpload(**dados_assinatura)
        db.session.add(assinatura)
        db.session.commit()
        return assinatura