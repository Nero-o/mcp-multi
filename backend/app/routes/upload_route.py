from flask import Blueprint, g, current_app, request, jsonify

from app.controllers.upload_controller import upload_file, upload_json_data, upload_form
from app.utils.decorators import role_required, login_required
from app.services.quadro_alerta_service import QuadroAlertaService

upload_bp = Blueprint('upload', __name__)

@upload_bp.route("/upload-form", methods=["POST"])
@login_required()
@role_required(["ParceiroAdministrador", "Administrador", 'Parceiro'])
def upload_formulario():
    usuario_logado = g.user_data
    tenant_url = g.tenant_url
    
    response, status_code = upload_form(
        request=request,
        usuario_logado=usuario_logado,
        tenant_url=tenant_url,
        tipo_upload="Formulario"
    )
    return response, status_code



@upload_bp.route("/upload", methods=["POST"])
@login_required()
@role_required(["ParceiroAdministrador", "Administrador", 'Parceiro']) 
def upload_documento():
    ## BUSCAR ID DO COOKIE EM UM DECORATOR
    usuario_logado = g.user_data
    tenant_url = g.tenant_url
    response, status_code = upload_file(
        request=request,
        usuario_logado=usuario_logado, 
        tenant_url=tenant_url,
        tipo_upload="CSV"
    )
    return response, status_code

@upload_bp.route("/upload-json", methods=["POST"])
@login_required()
@role_required(["ParceiroAdministrador", "Administrador", 'Parceiro'])
def upload_json():
    usuario_logado = g.user_data
    tenant_url = g.tenant_url
    
    if not request.is_json:
        return jsonify({"error": "Requisição deve ser JSON"}), 400
        
    response, status_code = upload_json_data(
        request=request,
        usuario_logado=usuario_logado,
        tenant_url=tenant_url,
        tipo_upload="API"
    )
    return response, status_code


@upload_bp.route("/get-status-upload", methods=["GET"])
def get_status_upload():
    quadro_alerta_id = request.args.get('id')

    if not quadro_alerta_id:
        return jsonify({'msg': 'ID da quadro alerta não fornecido.'}), 400

    quadro_alerta = QuadroAlertaService.get_quadro_alerta_por_id(quadro_alerta_id)


    obj_return = {
        'id': quadro_alerta.id,
        'texto': quadro_alerta.texto,
        'dados_extras': quadro_alerta.dados_extras,
        'titulo': quadro_alerta.titulo,
        'tipo': quadro_alerta.tipo
    }
    ## SE FOR IMPLEMENTAR MESMO ISSO, REMOVER O CODIGO ABAIXO
    # obj_return['texto'] = 'Concluido'
    
    return jsonify(obj_return), 200
