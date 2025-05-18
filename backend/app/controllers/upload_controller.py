import datetime
import boto3
import csv
import io
import json
from flask import jsonify, current_app, Request
from werkzeug.test import EnvironBuilder
from werkzeug.datastructures import FileStorage, MultiDict
from app.config import Config
from app.services.quadro_alerta_service import QuadroAlertaService
from app.services.assinatura_upload_service import AssinaturaUploadService
from app.controllers.usuario_controller import UsuarioController
from app.utils.helpers import force_str_to_date_obj
from app.utils.valida_arquivo import valida_arquivos
from app.utils.hash import create_hash_assinatura


# Configurações da AWS
AWS_S3_BUCKET = Config.AWS_S3_BUCKET
AWS_SQS_QUEUE_URL = Config.AWS_SQS_QUEUE_URL

s3_client = boto3.client('s3',region_name=Config.AWS_REGION)
sqs_client = boto3.client('sqs',region_name=Config.AWS_REGION)


def upload_form(request, usuario_logado, tenant_url, tipo_upload='Formulario'):
    try:
        logger = current_app.logger
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({"error": "Requisição inválida. [1]"}), 400
        
        form_data = {
            "cnpj_sacado": request_data.get("cnpj_sacado"),
            "email_sacado": request_data.get("email_sacado"),
            "sacado": request_data.get("sacado"),
            "socio_representante": request_data.get("socio_representante"),
            "cpf_representante": request_data.get("cpf_representante"),
            "email_representante": request_data.get("email_representante"),
            "telefone": request_data.get("telefone"),
            "razao_social": request_data.get("razao_social"),
            "nome_fantasia": request_data.get("nome_fantasia"),
            "cpf_cnpj": request_data.get("cpf_cnpj"),
            "email": request_data.get("email"),
            "endereco": request_data.get("endereco"),
            "numero": request_data.get("numero"),
            "compl": request_data.get("complemento"),
            "bairro": request_data.get("bairro"),
            "cep": request_data.get("cep"),
            "municipio": request_data.get("municipio"),
            "uf": request_data.get("uf"),
            "bco": request_data.get("bco"),
            "agencia": request_data.get("agencia"),
            "conta": request_data.get("conta"),
            "tipo_chave": request_data.get("tipo_chave"),
            "chavepix": request_data.get("chavepix"),
            "documento": request_data.get("documento"),
            "tipo_doc": request_data.get("tipo_doc"),
            "titulo": request_data.get("titulo"),
            "dt_emis": request_data.get("dt_emis"),
            "dt_fluxo": request_data.get("dt_fluxo"),
            "vlr_face": request_data.get("vlr_face"),
            "parcelas": request_data.get("parcelas"),
            "tipo_operacao": request_data.get("tipo_operacao", "parceiro_sacado"),
            "metodo_assinatura": request_data.get("metodo_assinatura", "aeco")
        }
        
        if form_data["tipo_operacao"] == "parceiro_cedente":
            form_data["parceiro_cedente"] = 1
        else:
            form_data["parceiro_cedente"] = 0


        # Remover campos vazios
        form_data = {k: v for k, v in form_data.items() if v is not None and v != ""}

        if 'dt_emis' in form_data:
            date_obj = force_str_to_date_obj(form_data['dt_emis'])
            if hasattr(date_obj, 'strftime'):
                form_data['dt_emis'] = date_obj.strftime('%d/%m/%Y')
                
        if 'dt_fluxo' in form_data:
            date_obj = force_str_to_date_obj(form_data['dt_fluxo'])
            if hasattr(date_obj, 'strftime'):
                form_data['dt_fluxo'] = date_obj.strftime('%d/%m/%Y')

        payload = {
            "data": [form_data]
        }
        
        # Criar uma nova request com os dados convertidos
        builder = EnvironBuilder(
            method='POST',
            path='/upload-json',
            json=payload,
            headers={k: v for k, v in request.headers.items()}
        )
        form_request = Request(builder.get_environ())
        
        # Usar o mesmo processamento da rota upload-json
        response, status_code = upload_json_data(
            request=form_request,
            usuario_logado=usuario_logado,
            tenant_url=tenant_url,
            tipo_upload=tipo_upload
        )
        return response, status_code
        
    except Exception as e:
        current_app.logger.error(f"Erro ao processar formulário: {str(e)}")
        return jsonify({
            "error": "Erro ao processar dados do formulário",
            "details": str(e)
        }), 500

def upload_json_data(request, usuario_logado, tenant_url, tipo_upload=None):
    logger = current_app.logger
    try:
        # Validar se há dados
        json_data = request.get_json()
        if not json_data or 'data' not in json_data or not json_data['data']:
            return jsonify({"error": "Dados não fornecidos"}), 400

        # Pegar headers dinamicamente do primeiro item
        headers = list(json_data['data'][0].keys())

        # Criar arquivo CSV temporário
        csv_buffer = io.StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=headers, delimiter=';')
        writer.writeheader()
        
        for row in json_data['data']:
            writer.writerow(row)

        # Converter para FileStorage
        csv_buffer.seek(0)
        temp_file = FileStorage(
            stream=io.BytesIO(csv_buffer.getvalue().encode('latin1')),
            filename=f'upload_via_{tipo_upload.lower()}_{datetime.datetime.now().timestamp()}.csv',
            content_type='text/csv'
        )

        # Simular request com arquivo
        request.files = MultiDict([('file[]', temp_file)])
        
        # Usar o fluxo existente de upload
        return upload_file(
            request=request,
            usuario_logado=usuario_logado,
            tenant_url=tenant_url,
            tipo_upload=tipo_upload
        )

    except IndexError:
        logger.error("JSON data está vazio ou mal formatado")
        return jsonify({"error": "JSON data está vazio ou mal formatado"}), 400
    except Exception as e:
        logger.error(f"Erro ao processar upload via JSON: {str(e)}")
        return jsonify({"error": "Erro interno no servidor"}), 500

def upload_file(request, usuario_logado, tenant_url, tipo_upload=None):
    logger = current_app.logger
    try:
        
        if not tenant_url:
            return jsonify({"error": "Requisição inválida. 01"}), 400

        logger.info(f"Usuário logado: {usuario_logado}")

        # Verifica se há arquivos na requisição
        if 'file[]' in request.files:
            all_files = request.files.getlist("file[]")
        else:
            return jsonify({"error": "Nenhum arquivo fornecido"}), 400
        
        
        if len(all_files) == 0:
            return jsonify({"error": "Nenhum arquivo fornecido"}), 400
        elif len(all_files) > 1:
            return jsonify({"error": "Apenas um arquivo pode ser enviado por requisição"}), 400
        
        file = all_files[0]
        
        if request.is_json:
            logger.info(f"Request data JSON: {request.get_json()}")
            request_data = request.get_json()
        else:
            logger.info(f"Request data FORM: {request.form}")
            request_data = request.form

        print(f"Request data: {request_data}")

        # Valida os arquivos antes de prosseguir
        valido, mensagem, tipo = valida_arquivos([file])
        if not valido:
            return jsonify({"error": mensagem}), 400

        usuario = UsuarioController.get_user_db_logado(request, usuario_logado, tenant_url)
        
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado.'}), 401
        
        quadro_alerta = QuadroAlertaService.create_quadro_alerta({
            'titulo': f'Upload {tipo_upload}',
            'texto': 'Aguarde! Estamos lendo a remessa...', 
            'usuario_id': usuario.id,
            'tipo': tipo_upload,
        })
                
        obj_assinatura = {
            'usuario_id': usuario.id,
            'parceiro_id': usuario.parceiro_id,
            'ip':request.remote_addr,
        }
        
        assinatura_aux = create_hash_assinatura(obj_assinatura, 'upload')
        assinatura_aux.update(obj_assinatura)
        assinatura_upload = AssinaturaUploadService.registrar_assinatura_upload(assinatura_aux)

        logger.info(f"Quadro alerta criado com sucesso: {quadro_alerta.serialize()}")
        logger.info(f"Assinatura upload registrada com sucesso: {assinatura_upload.serialize()}")

        # Define a chave para o arquivo no S3
        s3_key = f'{tenant_url}/unprocessed/{datetime.datetime.now().timestamp()}-{file.filename}'

        logger.info(f"Enviando arquivo {file.filename} para o bucket {AWS_S3_BUCKET} com key {s3_key}")

        # Envia o arquivo para o S3
        s3_client.upload_fileobj(file, AWS_S3_BUCKET, s3_key)

        logger.info(f"Arquivo enviado com sucesso para o bucket {AWS_S3_BUCKET} com key {s3_key}")

        # Envia uma mensagem para a fila SQS com as informações do arquivo
        message_body = {
            's3_bucket': AWS_S3_BUCKET,
            's3_key': s3_key,
            'quadro_alerta_id': quadro_alerta.id,
            'metodo_assinatura': request_data.get("metodo_assinatura", "aeco"),
            'tipo_operacao': request_data.get("tipo_operacao", "parceiro_sacado")
        }

        response = sqs_client.send_message(
            QueueUrl=AWS_SQS_QUEUE_URL,
            MessageBody=json.dumps(message_body)
        )

        logger.info(f"Mensagem enviada para a fila SQS com ID: {response.get('MessageId')}")

        resultados = {
            'file': file.filename,
            's3_key': s3_key
        }

        return jsonify({
            "msg": "Arquivos enviados com sucesso.",
            "data": quadro_alerta.id,
            "resultados": resultados
        }), 200

    except Exception as e:
        logger.error(f"Erro ao processar upload: {str(e)}")
        return jsonify({"error": "Erro interno no servidor"}), 500