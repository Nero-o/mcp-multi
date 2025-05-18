# Import necessary modules
import csv
import io
import datetime
from flask import make_response, render_template, current_app
from sqlalchemy.orm import joinedload
from app.utils.formata_monetario import formata_monetario
from app.utils.envia_email import envia_email
from app.utils.enums import LINK_PORTAL
from app.models.fornecedor_nota_model import FornecedorNota
from app.controllers.parceiro_controller import ParceiroController
from app.controllers.usuario_controller import UsuarioController
from app.services.config_tenant_service import ConfigTenantService

def gera_retorno_csv(usuario_logado, tenant_url):
        
    csv_file, mensagem = generate_arquivo_retorno(
        usuario_logado=usuario_logado,
        tenant_url=tenant_url
    )
    if not csv_file:
        return False, mensagem

    # Generate a filename with the current date and time
    timestamp = datetime.datetime.now().strftime('%d%m%Y_%H%M%S')
    filename = f'arquivo_retorno_{timestamp}.csv'

    # Create a response object
    response = make_response(csv_file.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'

    if usuario_logado['role'] in ['Parceiro', 'ParceiroAdministrador']:
        usuario, mensagem = UsuarioController.valida_vinculo_usuario_parceiro_logado(usuario_logado, tenant_url)
        if not usuario:
            return False, mensagem

    # config_tenant = ConfigTenantService.get_config_por_tenant(tenant_url)
    # parceiro = ParceiroController.get_parceiro_por_tenant(tenant_url)

    # result, status_code = envia_email(
    #     destinatarios=[config_tenant['email_admin']],
    #     assunto=f"{parceiro.nome} - Arquivo de retorno",
    #     corpo=render_template(
    #         'email_arquivo_retorno.html',
    #         now=datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
    #         link_portal=LINK_PORTAL % parceiro.tenant_code
    #     ),
    #     anexos=[
    #         {
    #             'conteudo': csv_file.getvalue(),
    #             'nome': filename
    #         }
    #     ]
    # )
    # if status_code not in [202,200,'202','200']:
    #     current_app.logger.error(f"Erro ao enviar email ARQUIVO DE RETORNO para o parceiro. [backend/app/utils/arquivo_retorno.py]: {result}")
    #     return False, "Erro ao enviar email ARQUIVO DE RETORNO para o parceiro."
    
    return csv_file.getvalue(), "Arquivo de retorno gerado com sucesso."

def generate_arquivo_retorno(usuario_logado, tenant_url):
    parceiro = ParceiroController.get_parceiro_por_tenant(tenant_url)

    if usuario_logado['role'] in ['Parceiro', 'ParceiroAdministrador'] or usuario_logado['role'][0] in ['Parceiro', 'ParceiroAdministrador']:
        usuario, mensagem = UsuarioController.valida_vinculo_usuario_parceiro_logado(usuario_logado, tenant_url)
        if not usuario:
            return False, mensagem
        
    parceiro_id = parceiro.id

    # Define CSV columns (as before)
    columns = [
        'cnpj_sacado', 'cdcredor', 'razao_social', 'nome_fantasia', 'cpf_cnpj', 'email', 'endereco',
        'numero', 'compl', 'bairro', 'cep', 'municipio', 'uf', 'bco', 'agencia', 'conta', 'tipo_chave',
        'chavepix', 'documento', 'tipo_doc', 'titulo', 'dt_emis', 'dt_fluxo', 'vlr_face', 'vlr_disp_antec',
        'fator_desconto', 'desconto', 'desconto_juros_aeco', 'desconto_tac_aeco', 'desconto_banco_aeco',
        'taxa_total_aeco', 'valor_receber_aeco', 'valor_liquido', 'assinatura', 'data_assinatura',
        'data_conclusao', 'aeco_chavepix'
    ]

    # Create an in-memory file
    output = io.StringIO()
    # Initialize CSV writer
    writer = csv.DictWriter(output, fieldnames=columns, delimiter=';')
    writer.writeheader()

    # Query FornecedorNotas with status_id = 4
    notas = FornecedorNota.query.filter_by(
        status_id=4,
        parceiro_id=parceiro_id
    ).options(
        joinedload(FornecedorNota.fornecedor),
        joinedload(FornecedorNota.assinatura_nota),
        joinedload(FornecedorNota.parceiro)  # Assuming parceiro relationship exists
    ).all()

    for nota in notas:
        fornecedor = nota.fornecedor
        parceiro = nota.parceiro  # Assuming this relationship exists

        if fornecedor is None:
            continue  # Skip if no fornecedor associated

        # Access the single AssinaturaNota directly
        assinatura_nota = nota.assinatura_nota
        assinatura = assinatura_nota.assinatura if assinatura_nota else ''
        data_assinatura = assinatura_nota.data_cadastro if assinatura_nota else None

        separador_milhar = True
        separador_decimal = "."

        # Prepare data for CSV
        data = {
            'cnpj_sacado': nota.cnpj_sacado or '',
            'cdcredor': fornecedor.cdcredor.replace(".", "") or '',
            'razao_social': fornecedor.razao_social or '',
            'nome_fantasia': fornecedor.nome_fantasia or '',
            'cpf_cnpj': fornecedor.cpf_cnpj or '',
            'email': fornecedor.email or '',
            'endereco': fornecedor.endereco or '',
            'numero': fornecedor.numero or '',
            'compl': fornecedor.compl or '',
            'bairro': fornecedor.bairro or '',
            'cep': fornecedor.cep or '',
            'municipio': fornecedor.municipio or '',
            'uf': fornecedor.uf or '',
            'bco': fornecedor.bco or '',
            'agencia': fornecedor.agencia or '',
            'conta': fornecedor.conta or '',
            'tipo_chave': fornecedor.tipo_chave or '',
            'chavepix': fornecedor.chavepix or '',
            'documento': nota.documento or '',
            'tipo_doc': nota.tipo_doc or '',
            'titulo': nota.titulo or '',
            'dt_emis': nota.dt_emis.strftime('%d/%m/%Y') if nota.dt_emis else '',
            'dt_fluxo': nota.dt_fluxo.strftime('%d/%m/%Y') if nota.dt_fluxo else '',
            'vlr_face': formata_monetario(nota.vlr_face, separador_milhar, separador_decimal) or 0.0,
            'vlr_disp_antec': formata_monetario(nota.vlr_disp_antec, separador_milhar, separador_decimal) or 0.0,
            'fator_desconto': formata_monetario(nota.fator_desconto, separador_milhar, separador_decimal) or 0.0,
            'desconto': formata_monetario(nota.desconto, separador_milhar, separador_decimal) or 0.0,
            'desconto_juros_aeco': formata_monetario(nota.desconto_juros_aeco, separador_milhar, separador_decimal) or 0.0,
            'desconto_tac_aeco': formata_monetario(nota.desconto_tac_aeco, separador_milhar, separador_decimal) or 0.0,
            'desconto_banco_aeco': formata_monetario(nota.desconto_banco_aeco, separador_milhar, separador_decimal) or 0.0,
            'taxa_total_aeco': formata_monetario(nota.taxa_total_aeco, separador_milhar, separador_decimal) or 0.0,
            'valor_receber_aeco': formata_monetario(nota.valor_receber_aeco, separador_milhar, separador_decimal) or 0.0,
            'valor_liquido': formata_monetario(nota.valor_liquido, separador_milhar, separador_decimal) or 0.0,
            'assinatura': assinatura,
            'data_assinatura': data_assinatura.strftime('%d/%m/%Y %H:%M:%S') if data_assinatura else '',
            'data_conclusao': nota.data_conclusao.strftime('%d/%m/%Y %H:%M:%S') if nota.data_conclusao else '',
            'aeco_chavepix': ''
        }

        # Write data to CSV
        writer.writerow(data)

    # Move the cursor to the beginning of the StringIO object
    output.seek(0)
    return output, "Retorno gerado com sucesso."
