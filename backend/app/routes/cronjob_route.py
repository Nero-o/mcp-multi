from flask import Blueprint, request, g
from app.utils.decorators import login_required, role_required
from flask import jsonify
from app.controllers.cronjob_controller import CronjobController

cronjob_bp = Blueprint('cronjob', __name__)

@cronjob_bp.route('/calcula_nota', methods=['POST'])
@login_required()
@role_required(['Administrador'])  # Apenas Administrador
def calcula_nota():
    tenant_url = g.tenant_url
    cronjob_controller = CronjobController()
    return cronjob_controller.executar_task_cronjob('calcula_nota', tenant_url)

@cronjob_bp.route('/expiracao_nota', methods=['POST'])
@login_required()
@role_required(['Administrador'])  # Apenas Administrador
def expiracao_nota():
    tenant_url = g.tenant_url
    cronjob_controller = CronjobController()
    return cronjob_controller.executar_task_cronjob('expiracao_nota', tenant_url)





@cronjob_bp.route('/notificar_expiracao_nota', methods=['POST'])
@login_required()
@role_required(['Administrador', 'Parceiro', 'ParceiroAdministrador'])
def notificar_expiracao_nota():
    tenant_url = g.tenant_url
    cronjob_controller = CronjobController()
    return cronjob_controller.executar_task_cronjob('notificacao_nota_expirar_auto', tenant_url)

@cronjob_bp.route('/habilitar_fornecedores', methods=['POST'])
@login_required()
@role_required(['Administrador', 'Parceiro', 'ParceiroAdministrador'])
def habilitar_fornecedores():
    tenant_url = g.tenant_url
    cronjob_controller = CronjobController()
    return cronjob_controller.executar_task_cronjob('habilitar_fornecedor_auto', tenant_url)

@cronjob_bp.route('/retorno_automatico', methods=['POST'])
@login_required()
@role_required(['Administrador', 'Parceiro', 'ParceiroAdministrador'])
def retorno_automatico():
    tenant_url = g.tenant_url
    cronjob_controller = CronjobController()
    return cronjob_controller.executar_task_cronjob('habilitar_retorno_auto', tenant_url)


@cronjob_bp.route('/email_nota_disponivel', methods=['POST'])
@login_required()
@role_required(['Administrador', 'Parceiro', 'ParceiroAdministrador'])
def email_nota_disponivel():
    tenant_url = g.tenant_url
    cronjob_controller = CronjobController()
    return cronjob_controller.executar_task_cronjob('email_nota_disponivel', tenant_url)

@cronjob_bp.route('/notificacao_cadastro_incompleto', methods=['POST'])
@login_required()
@role_required(['Administrador', 'Parceiro', 'ParceiroAdministrador'])
def notificacao_cadastro_incompleto():
    tenant_url = g.tenant_url
    cronjob_controller = CronjobController()
    return cronjob_controller.executar_task_cronjob('notificacao_cadastro_incompleto', tenant_url)