from app.repositories.quadro_alerta_repository import QuadroAlertaRepository

class QuadroAlertaService:

    @staticmethod
    def get_all_quadro_alerta(filter=None):
        return QuadroAlertaRepository.get_all_quadro_alerta(filter)
    
    @staticmethod
    def get_quadro_alerta_por_id(quadro_alerta_id):
        return QuadroAlertaRepository.get_quadro_alerta_por_id(quadro_alerta_id)

    @staticmethod
    def get_quadro_alerta_por_usuario(usuario_id):
        return QuadroAlertaRepository.get_quadro_alerta_por_usuario(usuario_id)

    @staticmethod
    def create_quadro_alerta(dados):
        return QuadroAlertaRepository.create_quadro_alerta(dados)

    @staticmethod
    def update_quadro_alerta(quadro_alerta_id, dados):
        return QuadroAlertaRepository.update_quadro_alerta(quadro_alerta_id, dados)