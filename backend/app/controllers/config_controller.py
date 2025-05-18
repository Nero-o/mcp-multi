from flask import jsonify, current_app
from app.services.config_tenant_service import ConfigTenantService
from app.services.parceiro_service import ParceiroService
from app.services.usuario_service import UsuarioService
from app.controllers.usuario_controller import UsuarioController

class ConfigController:
    def __init__(self):
        self.service = ConfigTenantService()

    def create_config(self, data):
        self._transform_boolean_values(data)
        try:
            config = self.service.create_config(data)
            return jsonify({
                'message': 'Configuração criada com sucesso',
                'data': config
            }), 200
        except Exception as e:
            return jsonify({
                'error': 'Erro ao criar configuração',
                'message': str(e)
            }), 400

    def get_all_configs(self):
        try:
            configs = self.service.get_all_configs()
            return jsonify({
                'data': configs
            }), 200
        except Exception as e:
            return jsonify({
                'error': 'Erro ao buscar configurações',
                'message': str(e)
            }), 400

    def _get_config_parceiro_logado(self, usuario_logado, tenant_code):
        usuario_parceiro, mensagem = UsuarioController.valida_vinculo_usuario_parceiro_logado(
            usuario_logado,
            tenant_code
        )
        if not usuario_parceiro:
            return jsonify({
                'error': mensagem
            }), 404

        parceiro = ParceiroService.get_parceiro_por_id(usuario_parceiro.parceiro_id)
        config = ConfigTenantService.get_config_by_parceiro_id(parceiro.id)

        return config

    def get_config(self, config_id=None, usuario_logado=None, tenant_code=None):

        if usuario_logado and (usuario_logado['role'][0] == 'Parceiro' or usuario_logado['role'][0] == 'ParceiroAdministrador'):
            config = self._get_config_parceiro_logado(usuario_logado, tenant_code)

            if not config:
                return jsonify({
                    'error': 'Configuração não encontrada para este parceiro'
                }), 404

            return jsonify({
                'data': config
            }), 200
        
        try:
            config = self.service.get_config_por_id(config_id)
            if not config:
                return jsonify({
                    'message': 'Configuração não encontrada'
                }), 404
            return jsonify({
                'data': config
            }), 200
        except Exception as e:
            return jsonify({
                'error': 'Erro ao buscar configuração',
                'message': str(e)
            }), 400

    # def _transform_boolean_values(self, data):
    #     if isinstance(data, dict):
    #         for key, value in data.items():
    #             if isinstance(value, (dict, list)):
    #                 self._transform_boolean_values(value)
    #             elif isinstance(value, bool) or value in ['true', 'false', 'True', 'False']:
    #                 data[key] = 1 if str(value).lower() == 'true' else 0
    #     elif isinstance(data, list):
    #         for i, item in enumerate(data):
    #             if isinstance(item, (dict, list)):
    #                 self._transform_boolean_values(item)
    #             elif isinstance(item, bool) or item in ['true', 'false', 'True', 'False']:
    #                 data[i] = 1 if str(item).lower() == 'true' else 0

    

    def update_config(self, config_id, data):

        # self._transform_boolean_values(data)
        current_app.logger.info(f"Dados requisicao update_config: {data}")
        try:
            config = self.service.update_config(config_id, data)
            if not config:
                return jsonify({
                    'message': 'Configuração não encontrada'
                }), 404
            return jsonify({
                'message': 'Configuração atualizada com sucesso',
                'data': config
            }), 200
        except Exception as e:
            return jsonify({
                'error': 'Erro ao atualizar configuração',
                'message': str(e)
            }), 400

    def delete_config(self, config_id):
        try:
            deleted = self.service.delete_config(config_id)
            if not deleted:
                return jsonify({
                    'message': 'Configuração não encontrada'
                }), 404
            return jsonify({
                'message': 'Configuração excluída com sucesso'
            }), 200
        except Exception as e:
            return jsonify({
                'error': 'Erro ao excluir configuração',
                'message': str(e)
            }), 400