from app.services.quadro_alerta_service import QuadroAlertaService

class QuadroAlertaController:

    @staticmethod
    def get_all_quadro_alerta(filter=None):
        return QuadroAlertaService.get_all_quadro_alerta(filter)
    
    @staticmethod
    def get_quadro_alerta_por_id(quadro_alerta_id):
        return QuadroAlertaService.get_quadro_alerta_por_id(quadro_alerta_id)

    @staticmethod
    def get_quadro_alerta_por_usuario(usuario_id):
        return QuadroAlertaService.get_quadro_alerta_por_usuario(usuario_id)

    @staticmethod
    def create_quadro_alerta(dados):
        return QuadroAlertaService.create_quadro_alerta(dados)

    @staticmethod
    def update_quadro_alerta(quadro_alerta_id, dados):
        return QuadroAlertaService.update_quadro_alerta(quadro_alerta_id, dados)