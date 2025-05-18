from flask import Blueprint, request, g
from app.utils.decorators import login_required, role_required
from app.controllers.config_controller import ConfigController

config_bp = Blueprint('config', __name__)

@config_bp.route('/create_config', methods=['POST'])
@login_required()
@role_required(['Administrador', 'Parceiro', 'ParceiroAdministrador'])
def create_config():
    data = request.get_json()
    return ConfigController().create_config(data)

@config_bp.route('/lista_config', methods=['GET'])
@login_required()
@role_required(['Administrador', 'Parceiro', 'ParceiroAdministrador'])
def get_all_configs():
    return ConfigController().get_all_configs()

@config_bp.route('/detalhe_config', methods=['GET'])
@login_required()
@role_required(['Administrador', 'Parceiro', 'ParceiroAdministrador'])
def get_config():
    usuario_logado = g.user_data
    tenant_code = g.tenant_url
    config_id = request.args.get('config_id')

    return ConfigController().get_config(
        config_id=config_id,
        usuario_logado=usuario_logado,
        tenant_code=tenant_code
    )

@config_bp.route('/update_config', methods=['PUT'])
@login_required()
@role_required(['Administrador', 'Parceiro', 'ParceiroAdministrador'])
def update_config():
    config_id = request.args.get('config_id')
    data = request.get_json()
    return ConfigController().update_config(config_id, data)

@config_bp.route('/delete_config', methods=['DELETE'])
@login_required()
@role_required(['Administrador', 'Parceiro', 'ParceiroAdministrador'])
def delete_config():
    config_id = request.args.get('config_id')
    return ConfigController().delete_config(config_id)