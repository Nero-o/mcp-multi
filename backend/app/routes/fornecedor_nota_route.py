##app/routes/fornecedor_nota_route.py
from sqlalchemy.orm import joinedload
from flask import Blueprint, jsonify, g, request, current_app, render_template
from datetime import datetime
from app.controllers.fornecedor_nota_controller import FornecedorNotaController
from app.controllers.assinatura_fornecedor_nota_controller import AssinaturaFornecedorNotaController
from app.utils.decorators import login_required, role_required
from app.utils.arquivo_retorno import gera_retorno_csv
from app.utils.envia_email import envia_email
# from app.utils.twilio import envia_mensagem, gera_texto_whatsapp_nota_disponivel
from app.services.parceiro_service import ParceiroService
from app.services.fornecedor_parceiro_service import FornecedorParceiroService
from app.models.fornecedor_nota_model import FornecedorNota


fornecedor_nota_bp = Blueprint('fornecedor_nota', __name__)

@fornecedor_nota_bp.route('/get_parcelas', methods=['GET'])
@login_required()
def get_parcelas():
    nota_id = request.args.get('antecipacao_id', type=int)
    if not nota_id:
        return jsonify({'msg': 'ID da nota não fornecido.'}), 400

    resultado = FornecedorNotaController.get_parcelas(nota_id)
    return jsonify(resultado), 200


@fornecedor_nota_bp.route('/resumo-operacao', methods=['POST'])
@login_required()
def get_resumo_operacao():
    usuario_logado = g.user_data
    tenant_code = g.tenant_url
    notas_id = request.json.get('notas_id')
    
    resultado = AssinaturaFornecedorNotaController.get_resumo_operacao(usuario_logado, tenant_code, notas_id)
    if not resultado:
        return jsonify({'msg': 'Operação inválida.'}), 400
    
    if isinstance(resultado, tuple):
        return jsonify(resultado), resultado[1]
    
    
    return resultado, 200
@fornecedor_nota_bp.route('/contas_a_pagar', methods=['GET'])
@login_required()
@role_required(['Administrador', 'Parceiro', 'ParceiroAdministrador'])
def contas_a_pagar():
    usuario_logado = g.user_data
    tenant_url = g.tenant_url
    
    # Obter parâmetros de paginação
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        response, mensagem = FornecedorNotaController.contas_a_pagar(
            usuario_logado=usuario_logado,
            tenant_code_url=tenant_url,
            page=page,
            per_page=per_page
        )
        
        if not response:
            return jsonify({'msg': mensagem}), 400
            
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar contas a pagar: {str(e)}")
        return jsonify({'msg': 'Erro ao buscar contas a pagar'}), 400

@fornecedor_nota_bp.route('/contas_a_receber', methods=['GET'])
@login_required()
@role_required(['Administrador', 'Fornecedor', 'Parceiro', 'ParceiroAdministrador'])
def contas_a_receber():
    usuario_logado = g.user_data
    tenant_url = g.tenant_url
    
    # Obter parâmetros de paginação
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        response, mensagem = FornecedorNotaController.contas_a_receber(
            usuario_logado=usuario_logado,
            tenant_code_url=tenant_url,
            page=page,
            per_page=per_page
        )
        
        if not response:
            return jsonify({'msg': mensagem}), 400
            
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar contas a receber: {str(e)}")
        return jsonify({'msg': 'Erro ao buscar contas a receber'}), 400


# Nova rota para notas disponíveis
@fornecedor_nota_bp.route('/notas_disponiveis', methods=['GET'])
@login_required()
@role_required(['Administrador', 'Parceiro', 'ParceiroAdministrador'])
def notas_disponiveis():
    usuario_logado = g.user_data
    tenant_url = g.tenant_url

    # Obter o parceiro atual usando o tenant_url
    parceiro = ParceiroService.get_parceiro_por_tenant(tenant_url)
    if not parceiro:
        return jsonify({'msg': 'Parceiro não encontrado.'}), 404

    # Obter todos os fornecedores_parceiros habilitados (excluido == False)
    fornecedores_parceiros = FornecedorParceiroService.get_fornecedor_parceiro_por_parceiro_id(parceiro.id, excluido=0)
    # Obter os IDs dos fornecedores habilitados
    fornecedores_ids = [fp.fornecedor_id for fp in fornecedores_parceiros if fp.excluido == 0]

    current_app.logger.info(f"Fornecedores habilitados: {fornecedores_ids}")

    if not fornecedores_ids:
        return jsonify({'msg': 'Nenhum fornecedor habilitado encontrado.'}), 400

    # Buscar as notas com status_id == 1 para esses fornecedores e parceiro atual
    notas = FornecedorNota.query.options(joinedload(FornecedorNota.fornecedor)).filter(
        FornecedorNota.parceiro_id == parceiro.id,
        FornecedorNota.status_id == 1,
        FornecedorNota.fornecedor_id.in_(fornecedores_ids),
        FornecedorNota.excluido == 0  # Certificar-se de que a nota não está excluída
    ).all()

    if not notas:
        return jsonify({'msg': 'Nenhuma nota disponível encontrada.'}), 404

    # Agrupar notas por fornecedor
    notas_por_fornecedor = {}
    for nota in notas:
        fornecedor_id = nota.fornecedor_id
        if fornecedor_id not in notas_por_fornecedor:
            notas_por_fornecedor[fornecedor_id] = {
                'fornecedor': nota.fornecedor,
                'notas': []
            }
        notas_por_fornecedor[fornecedor_id]['notas'].append(nota)

    # Para cada fornecedor, enviar um e-mail personalizado
    sucesso_envio = True
    for fornecedor_id, dados in notas_por_fornecedor.items():
        fornecedor = dados['fornecedor']
        notas_do_fornecedor = dados['notas']

        if not fornecedor.email:
            continue  # Se o fornecedor não tem e-mail, pula para o próximo

        # Montar o corpo do e-mail usando o template HTML
        corpo_email = render_template(
            'email_nota_disponivel.html',
            fornecedor_nome=fornecedor.razao_social,
            notas=notas_do_fornecedor,
            link_portal=g.full_domain,
            parceiro=parceiro,
            ano_atual=datetime.now().year
        )
        # Destinatário de e-mail e número de telefone
        destinatario_email = fornecedor.email

        # Assunto do e-mail
        assunto = f"{parceiro.nome} - Notas Disponíveis"

        # Enviar o e-mail usando a função envia_email
        response_email, status_code = envia_email([destinatario_email], assunto, corpo_email)
        sucesso_email = status_code == 200
        
        # texto_whatsapp = gera_texto_whatsapp_nota_disponivel(fornecedor, notas_do_fornecedor)
        # response_whatsapp = envia_mensagem(fornecedor.telefone, texto_whatsapp)
        # sucesso_whatsapp = response_whatsapp

        if not sucesso_email:
            sucesso_envio = False  # Marca que houve falha em algum envio
        else:
            # Atualizar o campo 'email_disponivel' das notas para 1
            for nota in notas_do_fornecedor:
                try:
                    FornecedorNotaController.update_fornecedor_nota(nota.id, {"email_disponivel": 1})
                except Exception as e:
                    sucesso_envio = False
                    # Opcional: logar o erro
                    current_app.logger.error(f"Erro ao atualizar as notas do fornecedor {fornecedor_id}: {str(e)}")
                    
    if sucesso_envio:
        return jsonify({'msg': 'E-mails enviados com sucesso.'}), 200
    else:
        return jsonify({'msg': 'Ocorreram falhas ao enviar alguns e-mails.'}), 206
    

@fornecedor_nota_bp.route('/lista_fornecedor_nota', methods=['GET'])
@login_required()
def get_all():
    usuario_logado = g.user_data
    # Obter parâmetros de query, com valores padrão
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        lista_status = [1]
        response = FornecedorNotaController.get_all_fornecedor_nota_paginacao(lista_status, page, per_page, usuario_logado) 
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar todos os fornecedor_nota: {e}")
        return jsonify({'msg': f"Requisição inválida 1"}), 400
    
    if not response:
        current_app.logger.error(f"Erro ao buscar todos os fornecedor_nota: {e}")
        return jsonify({'msg': 'Requisição inválida 2'}), 400
    
    return jsonify(response), 200

@fornecedor_nota_bp.route('/lista_extrato_nota', methods=['GET'])
@login_required()
def extrato():
    usuario_logado = g.user_data
    # Obter parâmetros de query, com valores padrão
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        lista_status = [2, 3, 4, 5]
        response = FornecedorNotaController.get_all_fornecedor_nota_paginacao(lista_status, page, per_page, usuario_logado) 
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar todos os fornecedor_nota: {e}")
        return jsonify({'msg': f"Requisição inválida 1"}), 400
    
    if not response:
        current_app.logger.error(f"Erro ao buscar todos os fornecedor_nota: {e}")
        return jsonify({'msg': 'Requisição inválida 2'}), 400
    
    return jsonify(response), 200


@fornecedor_nota_bp.route('/detalhe_fornecedor_nota', methods=['GET'])
@login_required()
def detalhe_fornecedor_nota():
    usuario_logado = g.user_data
    fornecedor_nota_id = request.args.get('nota_id')
    if not fornecedor_nota_id:
        return jsonify({'msg': 'ID da nota não fornecido.'}), 400
    
    fornecedor_nota, mensagem = FornecedorNotaController.detalhe_fornecedor_nota(fornecedor_nota_id, usuario_logado, g.tenant_url)

    if fornecedor_nota:
        return jsonify(fornecedor_nota), 200
    return jsonify({'msg': f'{mensagem}'}), 400


@fornecedor_nota_bp.route('/assina_nota', methods=['POST'])
@login_required()
@role_required(['Fornecedor'])
def registra_assinatura_nota():

    try:
        # Verifica o Content-Type da requisição
        if request.content_type and 'application/json' in request.content_type:
            payload = request.get_json(), 'json'
        else:
            # Fallback para args quando não é JSON
            payload = request.args.get('nota_id'), 'args'
    except Exception as e:
        current_app.logger.error(f"Erro ao decodificar a requisição (assina_nota): {e}")
        return jsonify({'msg': 'Tipo de dados incorreto.'}), 400
    
    data, tipo = payload

    if tipo == 'json':
        notas_id = data.get('nota_ids') 
    else:
        notas_id = [data]

    if not notas_id:
        return jsonify({'msg': 'Nota não informada.', 'payload': payload}), 400
    
    usuario_logado = g.user_data
    tenant_code = g.tenant_url

    resultado, mensagem = AssinaturaFornecedorNotaController.registrar_assinatura_nota(usuario_logado, tenant_code, notas_id)

    if resultado:
        return jsonify({'msg': mensagem}), 200
    else:
        current_app.logger.error(f"Erro ao registrar a assinatura da nota - {mensagem}")
        return jsonify({'msg': mensagem}), 400
    
@fornecedor_nota_bp.route('/ativa_desativa_nota', methods=['POST'])
@login_required()
@role_required(['Administrador'])
def ativa_desativa_nota():
    nota_id = request.args.get('nota_id', type=int)
    if not nota_id:
        return jsonify({'msg': 'ID da nota não fornecido.'}), 400
    
    data = request.get_json()
    habilitado = data.get('habilitado')
    resultado, mensagem = FornecedorNotaController.ativa_desativa_nota(nota_id, habilitado)

    if resultado:
        return jsonify({'msg': mensagem}), 200
    else:
        current_app.logger.error(f"Erro ao ativar/desativar a nota - {mensagem}")
        return jsonify({'msg': mensagem}), 400
    

@fornecedor_nota_bp.route('/conclui_nota', methods=['POST'])
@login_required()
@role_required(['Administrador'])
def conclui_nota():
    nota_id = request.args.get('nota_id', type=int)
    if not nota_id:
        return jsonify({'msg': 'ID da nota não fornecido.'}), 400

    resultado, mensagem = FornecedorNotaController.conclui_nota(nota_id)
    if resultado:
        return jsonify({'msg': mensagem}), 200
    else:
        current_app.logger.error(f"Erro ao registrar a assinatura da nota - {mensagem}")
        return jsonify({'msg': mensagem}), 400

@fornecedor_nota_bp.route('/cancela_nota', methods=['POST'])
@login_required()
@role_required(['Administrador'])
def cancela_nota():
    nota_id = request.args.get('nota_id', type=int)
    if not nota_id:
        return jsonify({'msg': 'ID da nota não fornecido.'}), 400

    resultado, mensagem = FornecedorNotaController.cancela_nota(nota_id)
    if resultado:
        return jsonify({'msg': mensagem}), 200
    else:
        current_app.logger.error(f"Erro ao registrar a assinatura da nota - {mensagem}")
        return jsonify({'msg': mensagem}), 400
    

@fornecedor_nota_bp.route('/arquivo_retorno', methods=['GET'])
@login_required()
@role_required(['Administrador', 'Parceiro', 'ParceiroAdministrador'])
def download_arquivo_retorno():
    # Generate the CSV content
    usuario_logado = g.user_data
    tenant_url = g.tenant_url

    response, mensagem = gera_retorno_csv(usuario_logado, tenant_url)

    if not response:
        current_app.logger.error(f"Erro ao gerar o arquivo de retorno - {mensagem}")
        return jsonify({'msg': mensagem}), 400

    return response


@fornecedor_nota_bp.route('/update_status_admin_nota', methods=['POST'])
@login_required()
@role_required(['Administrador'])
def update_status_admin_nota():
    nota_id = request.args.get('nota_id', type=int)
    if not nota_id:
        return jsonify({'msg': 'ID da nota não fornecido.'}), 400

    status_id = request.args.get('status_id', type=int)
    if not status_id:
        return jsonify({'msg': 'ID do status não fornecido.'}), 400

    resultado, mensagem = FornecedorNotaController.update_status_admin_nota(nota_id, status_id)
    if resultado:
        return jsonify({'msg': mensagem}), 200