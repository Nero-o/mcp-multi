from app.repositories.assinatura_upload_repository import AssinaturaUploadRepository

class AssinaturaUploadService:
    
    @staticmethod
    def registrar_assinatura_upload(dados_assinatura):
        return AssinaturaUploadRepository.registrar_assinatura_upload(dados_assinatura)
