import os
import base64
import json
import requests
import logging
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from app.services.fornecedor_nota_service import FornecedorNotaService
from app.models.fornecedor_nota_model import FornecedorNota
from app.services.parceiro_service import ParceiroService
from flask import g, current_app
from xhtml2pdf import pisa
import io

try:
    from app.services.d4sign_webhook_service import D4SignWebhookService
except Exception as e:
    pass

load_dotenv()

# Configuração do logger
logger = logging.getLogger('d4sign_service')

class D4SignService:
    def __init__(self):
        self._init_config()
        
    def _init_config(self):
        """Inicializa as configurações do serviço"""
        self.api_url = os.getenv('D4SIGN_API_URL', 'https://sandbox.d4sign.com.br/api/v1')
        self.api_token = os.getenv('D4SIGN_API_TOKEN')
        self.api_crypto_key = os.getenv('D4SIGN_CRYPTO_KEY')
        self.safe_id = os.getenv('D4SIGN_SAFE_ID')  # UUID do cofre onde os documentos serão armazenados
        
        # Configurar ambiente de templates
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        logger.info(f"D4Sign Service inicializado. API URL: {self.api_url}")
    
    def _get_headers(self):
        """Retorna os headers para as requisições à API"""
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'tokenAPI': self.api_token,
            'cryptKey': self.api_crypto_key
        }
    
    def _handle_response(self, response, operation_name="operação"):
        """Trata as respostas da API"""
        logger.info(f"D4Sign {operation_name} - Status: {response.status_code}")
        
        if response.status_code >= 200 and response.status_code < 300:
            if not response.text.strip():
                logger.info(f"D4Sign {operation_name} - Resposta vazia, mas bem-sucedida")
                return {"success": True}
            try:
                result = response.json()
                logger.info(f"D4Sign {operation_name} - Resposta processada com sucesso")
                return result
            except json.JSONDecodeError:
                logger.warning(f"D4Sign {operation_name} - Resposta não é um JSON válido: {response.text[:100]}...")
                return {"success": True, "raw_response": response.text}
        else:
            error_msg = f"Erro na requisição de {operation_name}: {response.status_code} - {response.text[:200]}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _generate_html_content(self, nota: FornecedorNota) -> str:
        """Gera o conteúdo HTML com os dados da nota para assinatura"""
        logger.info(f"Gerando conteúdo HTML para nota ID: {nota.id}")
        template = self.jinja_env.get_template('assinatura_d4sign.html')
        return template.render(nota=nota)
    
    def _convert_html_to_pdf(self, html_content: str) -> bytes:
        """Converte o conteúdo HTML para PDF usando xhtml2pdf"""
        logger.info("Iniciando conversão de HTML para PDF")
        try:
            # Cria um buffer para o PDF
            pdf_buffer = io.BytesIO()
            
            # Converte HTML para PDF
            pisa_status = pisa.CreatePDF(
                html_content,  # HTML como string
                dest=pdf_buffer
            )
            
            # Verifica se a conversão foi bem-sucedida
            if pisa_status.err:
                logger.error(f"Erro na conversão HTML para PDF: {pisa_status.err}")
                raise Exception("Erro ao converter HTML para PDF")
                
            # Retorna ao início do buffer
            pdf_buffer.seek(0)
            pdf_content = pdf_buffer.read()
            pdf_size_kb = len(pdf_content) / 1024
            logger.info(f"Conversão para PDF concluída. Tamanho: {pdf_size_kb:.2f} KB")
            return pdf_content
        
        except Exception as e:
            logger.error(f"Erro na conversão HTML para PDF: {str(e)}")
            raise
    
    def find_or_create_tenant_folder(self) -> str:
        """Busca pasta do tenant atual ou cria se não existir."""
        try:
            tenant_url = g.tenant_url
            logger.info(f"Buscando/criando pasta para tenant: {tenant_url}")
            
            # Buscar informações do parceiro (tenant)
            parceiro = ParceiroService.get_parceiro_por_tenant(tenant_url)
            if not parceiro:
                logger.error(f"Parceiro com tenant_code {tenant_url} não encontrado")
                raise Exception(f"Parceiro com tenant_code {tenant_url} não encontrado")
            
            # Nome da pasta será o tenant_url
            tenant_folder_name = tenant_url.strip()
            logger.info(f"Nome da pasta para o tenant: {tenant_folder_name}")
            
            # Listar pastas existentes no cofre
            url = f"{self.api_url}/folders/{self.safe_id}/find"
            logger.info(f"Buscando pastas no cofre D4Sign: {url}")
            response = requests.get(url, headers=self._get_headers())
            folders = self._handle_response(response, "listagem de pastas")
            
            # Verificar se a pasta do tenant já existe
            current_app.logger.info(f"Pastas encontradas: {folders}")
            if isinstance(folders, list):
                for folder in folders:
                    folder_name = folder.get("name")
                    if folder_name and folder_name.strip() == tenant_folder_name:
                        tenant_folder_uuid = folder.get("uuid_folder")  # Observe que é uuid_folder, não uuid
                        logger.info(f"Pasta do tenant '{tenant_folder_name}' encontrada com UUID: {tenant_folder_uuid}")
                        return tenant_folder_uuid
            # Também verificar se é um dicionário com 'data' (caso a API mude)
            elif isinstance(folders, dict) and "data" in folders:
                for folder in folders["data"]:
                    folder_name = folder.get("name")
                    if folder_name and folder_name.strip() == tenant_folder_name:
                        tenant_folder_uuid = folder.get("uuid_folder") or folder.get("uuid")
                        logger.info(f"Pasta do tenant '{tenant_folder_name}' encontrada com UUID: {tenant_folder_uuid}")
                        return tenant_folder_uuid
            
            # Se chegou aqui, a pasta não foi encontrada
            logger.info(f"Pasta do tenant '{tenant_folder_name}' não encontrada. Criando nova pasta...")
            url = f"{self.api_url}/folders/{self.safe_id}/create"
            payload = {
                "folder_name": tenant_folder_name
            }
            response = requests.post(url, headers=self._get_headers(), json=payload)
            result = self._handle_response(response, "criação de pasta")
            if isinstance(result, dict):
                tenant_folder_uuid = (
                    result.get("uuid_folder") or 
                    result.get("uuid") or 
                    (result.get("data", {}) or {}).get("uuid_folder") or
                    (result.get("data", {}) or {}).get("uuid")
                )
            else:
                tenant_folder_uuid = None
        
            
            if not tenant_folder_uuid:
                logger.error("UUID da pasta não retornado pela API na criação")
                raise Exception("Falha ao criar pasta do tenant: UUID não retornado")
                
            logger.info(f"Pasta do tenant '{tenant_folder_name}' criada com UUID: {tenant_folder_uuid}")
            return tenant_folder_uuid
        
        except Exception as e:
            logger.error(f"Erro ao buscar/criar pasta do tenant: {str(e)}")
            raise
    
    def upload_document(self, nota_id: int) -> Dict:
        """Faz upload do documento para a D4Sign na pasta do tenant."""
        start_time = datetime.now()
        logger.info(f"Iniciando upload de documento para nota ID: {nota_id}")
        
        try:
            nota = FornecedorNotaService.get_fornecedor_nota_por_id(nota_id)
            if not nota:
                logger.error(f"Nota ID {nota_id} não encontrada")
                raise Exception(f"Nota ID {nota_id} não encontrada")
                
            logger.info(f"Preparando documento para nota {nota_id} (Fornecedor: {nota.fornecedor.razao_social}, Sacado: {nota.sacado})")
            document_html = self._generate_html_content(nota)
            
            # Obter ou criar a pasta do tenant
            tenant_folder_uuid = self.find_or_create_tenant_folder()
            
            # Converte HTML para PDF
            logger.info("Convertendo HTML para PDF...")
            pdf_content = self._convert_html_to_pdf(document_html)
            
            # Converte o PDF para base64
            document_base64 = base64.b64encode(pdf_content).decode('utf-8')
            logger.info(f"Documento convertido para base64. Tamanho string: {len(document_base64)} caracteres")
            
            # Nome do documento mais descritivo
            doc_name = f"Antecipacao_{nota.fornecedor.razao_social.replace(' ', '_')}_{nota.id}_{datetime.now().strftime('%Y%m%d')}.pdf"
            doc_name = doc_name.replace("/", "_").replace("\\", "_")[:100]  # Limita tamanho e remove caracteres problemáticos
            
            # Upload do documento para a pasta do tenant
            url = f"{self.api_url}/documents/{self.safe_id}/uploadbinary"
            logger.info(f"Enviando documento '{doc_name}' para a pasta {tenant_folder_uuid}")
            
            payload = {
                'base64_binary_file': document_base64,
                'mime_type': 'application/pdf',
                'name': doc_name,
                'uuid_folder': tenant_folder_uuid  # Especifica a pasta do tenant
            }
            
            response = requests.post(url, headers=self._get_headers(), json=payload)
            result = self._handle_response(response, "upload de documento")
            
            # Armazenar UUID do documento retornado pela D4Sign
            uuid_documento = result.get('uuid')
            if not uuid_documento:
                logger.error("UUID do documento não retornado pela API")
                raise Exception("UUID do documento não retornado pela API")
            
            elapsed_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Upload do documento concluído em {elapsed_time:.2f}s. UUID: {uuid_documento}")
            
            return {
                'document_uuid': uuid_documento,
                'status': 'uploaded',
                'folder_uuid': tenant_folder_uuid,
                'document_name': doc_name
            }
            
        except Exception as e:
            logger.error(f"Erro ao fazer upload do documento: {str(e)}")
            raise
    
    def add_signers(self, document_uuid: str, nota: FornecedorNota) -> Dict:
        """Adiciona os signatários ao documento"""
        logger.info(f"Adicionando signatários ao documento {document_uuid}")
        
        try:
            # Validar dados dos signatários
            if not nota.fornecedor.email:
                logger.error(f"Email do fornecedor não encontrado para a nota {nota.id}")
                raise Exception(f"Email do fornecedor não encontrado para a nota {nota.id}")
                
            if not nota.email_sacado:
                logger.error(f"Email do sacado não encontrado para a nota {nota.id}")
                raise Exception(f"Email do sacado não encontrado para a nota {nota.id}")
            
            # Adicionar signatários
            url = f"{self.api_url}/documents/{document_uuid}/createlist"
            
            # Preparar dados dos signatários com limpeza de formatação
            fornecedor_cpf_cnpj = nota.fornecedor.cpf_cnpj.replace('.', '').replace('-', '').replace('/', '')
            sacado_cnpj = nota.cnpj_sacado.replace('.', '').replace('-', '').replace('/', '')
            
            logger.info(f"Signatário 1: {nota.fornecedor.razao_social} ({nota.fornecedor.email})")
            logger.info(f"Signatário 2: {nota.sacado} ({nota.email_sacado})")
            
            signers = [
                {
                    'email': nota.fornecedor.email,
                    'act': '1',  # 1 = assinar
                    'foreign': '0',
                    'certificadoicpbr': '0',  # 0 = não usar certificado ICP-Brasil
                    'name': nota.fornecedor.razao_social,
                    'documentation': fornecedor_cpf_cnpj,
                    'birthday': '',  # Opcional
                    'phone': ''  # Opcional
                },
                {
                    'email': nota.email_sacado,
                    'act': '1',
                    'foreign': '0',
                    'certificadoicpbr': '0',
                    'name': nota.sacado,
                    'documentation': sacado_cnpj,
                    'birthday': '',
                    'phone': ''
                }
            ]
            
            payload = {
                'signers': signers
            }
            
            response = requests.post(url, headers=self._get_headers(), json=payload)
            result = self._handle_response(response, "adição de signatários")
            
            logger.info(f"Signatários adicionados com sucesso ao documento {document_uuid}")
            
            return {
                'status': 'signers_added',
                'document_uuid': document_uuid,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Erro ao adicionar signatários: {str(e)}")
            raise
    
    def send_to_sign(self, document_uuid: str, skip_email: bool = False) -> Dict:
        """Envia documento para assinatura"""
        logger.info(f"Enviando documento {document_uuid} para assinatura. Skip email: {skip_email}")
        
        try:
            url = f"{self.api_url}/documents/{document_uuid}/sendtosigner"
            
            payload = {
                'message': 'Documento para assinatura - Operação de Antecipação',
                'workflow': '0',  # 0 = assinaturas simultâneas
                'skip_email': '1' if skip_email else '0'  # 1 = não enviar e-mail automático
            }
            
            response = requests.post(url, headers=self._get_headers(), json=payload)
            result = self._handle_response(response, "envio para assinatura")
            
            logger.info(f"Documento {document_uuid} enviado para assinatura com sucesso")
            
            return {
                'status': 'sent_to_sign',
                'document_uuid': document_uuid,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Erro ao enviar para assinatura: {str(e)}")
            raise
    
    def get_document_status(self, document_uuid: str) -> Dict:
        """Verifica o status atual do documento e suas assinaturas"""
        logger.info(f"Verificando status do documento {document_uuid}")
        
        try:
            url = f"{self.api_url}/documents/{document_uuid}/list"
            
            response = requests.get(url, headers=self._get_headers())
            result = self._handle_response(response, "verificação de status")
            
            # Interpretar o status e registrar no log
            if "data" in result and len(result["data"]) > 0:
                status = result["data"][0].get("status")
                logger.info(f"Status atual do documento {document_uuid}: {status}")
            
            return {
                'document_status': 'processing',
                'document_details': result
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar status do documento: {str(e)}")
            raise
    
    def create_signature_request(self, nota_id: int) -> Dict[str, str]:
        """Cria requisição de assinatura completa usando a D4Sign"""
        start_time = datetime.now()
        transaction_id = f"d4sign-{nota_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"[{transaction_id}] Iniciando processo de assinatura completa para nota {nota_id}")
        
        try:
            # Obter nota
            nota = FornecedorNotaService.get_fornecedor_nota_por_id(nota_id)
            if not nota:
                logger.error(f"[{transaction_id}] Nota com ID {nota_id} não encontrada")
                raise Exception(f"Nota com ID {nota_id} não encontrada")
            
            tenant = g.tenant_url
            logger.info(f"[{transaction_id}] Tenant: {tenant}, Fornecedor: {nota.fornecedor.razao_social}, Sacado: {nota.sacado}")
            
            # Upload do documento na pasta do tenant
            upload_result = self.upload_document(nota_id)
            document_uuid = upload_result.get('document_uuid')
            document_name = upload_result.get('document_name')
            logger.info(f"[{transaction_id}] Documento '{document_name}' enviado com UUID: {document_uuid}")
            
            # Adicionar signatários
            self.add_signers(document_uuid, nota)
            logger.info(f"[{transaction_id}] Signatários adicionados ao documento {document_uuid}")
            
            # # Configurar webhook para receber eventos do documento
            # webhook_result = D4SignWebhookService.register_webhook(
            #     document_uuid=document_uuid,
            #     tenant_url=tenant,
            #     api_url=self.api_url,
            #     headers=self._get_headers()
            # )
            # logger.info(f"[{transaction_id}] Webhook configurado: {webhook_result.get('status')}")
            
            # Enviar para assinatura
            self.send_to_sign(document_uuid)
            logger.info(f"[{transaction_id}] Documento enviado para assinatura")
            
            # URL direta para o documento
            document_url = f"{self.api_url.replace('/api/v1', '')}/docs/document/{document_uuid}"
            
            elapsed_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"[{transaction_id}] Processo de assinatura concluído em {elapsed_time:.2f}s. URL: {document_url}")
            
            return {
                'document_uuid': document_uuid,
                'status': 'created',
                'document_url': document_url,
                'document_name': document_name,
                'folder_uuid': upload_result.get('folder_uuid'),
                'transaction_id': transaction_id
            }
            
        except Exception as e:
            logger.error(f"[{transaction_id}] Erro ao criar requisição de assinatura: {str(e)}")
            raise
