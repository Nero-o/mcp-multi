import os
import base64
import urllib.parse
from typing import Dict
from dotenv import load_dotenv
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Document, Signer, SignHere, Tabs, RecipientViewRequest
from docusign_esign.client.api_exception import ApiException
from jinja2 import Environment, FileSystemLoader
from app.services.fornecedor_nota_service import FornecedorNotaService
from app.models.fornecedor_nota_model import FornecedorNota

load_dotenv()

class DocuSignService:
    def __init__(self):
        self._init_config()
        self.api_client = self._get_api_client()

    def _init_config(self):
        """Inicializa as configurações do serviço"""
        self.consent_url_base = "https://developers.docusign.com/platform/auth/consent"
        self.api_host = os.getenv('DS_API_HOST', 'https://demo.docusign.net/restapi')
        self.api_base_path = os.getenv('DS_API_BASE_PATH', '/restapi')
        self.client_id = os.getenv('DS_CLIENT_ID')
        self.client_secret = os.getenv('DS_CLIENT_SECRET')
        self.account_id = os.getenv('DS_ACCOUNT_ID')
        self.user_id = os.getenv('DS_USER_ID')
        self.private_key_path = os.getenv('DS_PRIVATE_KEY_PATH')
        self.auth_server = os.getenv('DS_AUTH_SERVER', 'account-d.docusign.com')
        self.auth_token = ""
        self.scopes = ["signature", "impersonation"]
        
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    def get_private_key(self):
        """Lê e retorna a chave privada do arquivo"""
        with open(self.private_key_path, 'r') as key_file:
            return key_file.read()

    def _get_jwt_token(self, api_client, retry_consent=True):
        """Obtém token JWT com retry para consentimento"""
        try:
            return api_client.request_jwt_user_token(
                client_id=self.client_id,
                user_id=self.user_id,
                oauth_host_name=self.auth_server,
                private_key_bytes=self.get_private_key(),
                expires_in=3600,
                scopes=self.scopes
            )
        except Exception as e:
            if retry_consent and "consent_required" in str(e).lower():
                return self.set_consent_if_required(api_client)
            raise

    def set_consent_if_required(self, api_client):
        """Configura o consentimento quando necessário"""
        consent_url = (
            f"https://{self.auth_server}/oauth/auth"
            f"?response_type=code"
            f"&scope=signature+impersonation"
            f"&client_id={self.client_id}"
            f"&redirect_uri={urllib.parse.quote(self.consent_url_base, safe='')}"
        )
        
        print("\nDados de configuração:")
        print(f"Auth Server: {self.auth_server}")
        print(f"Client ID: {self.client_id}")
        print(f"Scopes: signature+impersonation")
        print(f"Redirect URI: {self.consent_url_base}")
        print(f"\nURL de consentimento completa:\n{consent_url}\n")
        
        input("Depois de dar consentimento, pressione Enter para continuar...")
        return self._get_jwt_token(api_client, retry_consent=False)

    def _get_api_client(self):
        """Configura e retorna cliente API autenticado"""
        api_client = ApiClient()
        api_client.host = self.api_host
        api_client.set_base_path(self.api_base_path)
        
        try:
            response = self._get_jwt_token(api_client)
            self.auth_token = response.access_token
            api_client.set_default_header("Authorization", f"Bearer {self.auth_token}")
            api_client.set_default_header("Content-Type", "application/json")
            return api_client
        except Exception as e:
            raise Exception(f"Erro na configuração do cliente API: {str(e)}")

    def _create_signer(self, email, name, recipient_id, routing_order, anchor_string):
        """Cria configuração do signatário"""
        sign_here = SignHere(
            anchor_string=anchor_string,
            anchor_units="pixels",
            anchor_y_offset="0",
            anchor_x_offset="0"
        )
        
        signer = Signer(
            email=email,
            name=name,
            recipient_id=recipient_id,
            routing_order=routing_order,
            client_user_id=f'{recipient_id}'
        )
        signer.tabs = Tabs(sign_here_tabs=[sign_here])
        return signer

    def get_envelope_status(self, envelope_id: str) -> dict:
        """Verifica o status atual do envelope e suas assinaturas"""
        try:
            envelope_api = EnvelopesApi(self.api_client)
            envelope = envelope_api.get_envelope(
                account_id=self.account_id,
                envelope_id=envelope_id
            )
            
            recipients = envelope_api.list_recipients(
                account_id=self.account_id,
                envelope_id=envelope_id
            )
            
            status_info = {
                'envelope_status': envelope.status,
                'cedente_status': None,
                'sacado_status': None
            }
            
            for signer in recipients.signers:
                if signer.routing_order == '1':
                    status_info['cedente_status'] = signer.status
                elif signer.routing_order == '2':
                    status_info['sacado_status'] = signer.status
                    
            return status_info
            
        except ApiException as e:
            print(f"Erro ao verificar status do envelope: {str(e)}")
            raise

    def get_embedded_signing_url(self, envelope_id: str, signer_email: str, signer_name: str, recipient_id: str) -> str:
        """Gera uma URL para assinatura embedded do documento"""
        try:
            envelope_api = EnvelopesApi(self.api_client)
            
            return_url = (
                "https://aeco.homolog.riscosacado.aeco.app.br/api/docusign/callback"
                f"?envelope_id={envelope_id}"
                f"&signer_type={'cedente' if recipient_id=='1' else 'sacado'}"
            )

            recipient_view_request = RecipientViewRequest(
                authentication_method="none",
                client_user_id=f"100{recipient_id}",
                recipient_id=recipient_id,
                return_url=return_url,
                user_name=signer_name,
                email=signer_email
            )

            results = envelope_api.create_recipient_view(
                account_id=self.account_id,
                envelope_id=envelope_id,
                recipient_view_request=recipient_view_request
            )

            return results.url

        except ApiException as e:
            print(f"Erro ao gerar URL de assinatura: {str(e)}")
            print(f"Body da resposta: {e.body if hasattr(e, 'body') else 'Sem body'}")
            raise

    def create_signature_request(self, nota_id: int, event_notification: dict) -> Dict[str, str]:
        """Cria requisição de assinatura"""
        try:
            nota = FornecedorNotaService.get_fornecedor_nota_por_id(nota_id)
            document_html = self._generate_html_content(nota)
            
            document = Document(
                document_base64=base64.b64encode(document_html.encode('utf-8')).decode('utf-8'),
                name=f'documento_{nota_id}.html',
                file_extension='html',
                document_id='1'
            )

            signer1 = self._create_signer(
                nota.fornecedor.email, 
                nota.fornecedor.razao_social, 
                '1', '1', "/sn1/"
            )
            signer2 = self._create_signer(
                nota.email_sacado, 
                nota.sacado, 
                '2', '2', "/sn2/"
            )

            envelope_definition = EnvelopeDefinition(
                email_subject="Documento para Assinatura - Operação de Antecipação",
                email_blurb="Por favor, assine o documento anexo referente à operação de antecipação.",
                documents=[document],
                recipients={"signers": [signer1, signer2]},
                event_notifications=[event_notification],
                status="sent"
            )

            envelope_api = EnvelopesApi(self.api_client)
            result = envelope_api.create_envelope(
                account_id=self.account_id,
                envelope_definition=envelope_definition
            )

            signing_url_cedente = self.get_embedded_signing_url(
                result.envelope_id,
                nota.fornecedor.email,
                nota.fornecedor.razao_social,
                '1'
            )

            return {
                'envelope_id': result.envelope_id,
                'status': 'created',
                'signing_url_cedente': signing_url_cedente,
                'signing_url_sacado': None
            }

        except Exception as e:
            print(f"Erro ao criar envelope: {str(e)}")
            raise

    def _generate_html_content(self, nota: FornecedorNota) -> str:
        """Gera o conteúdo HTML com os dados da nota para assinatura"""
        template = self.jinja_env.get_template('assinatura_docusign.html')
        return template.render(nota=nota)

    def get_sacado_signing_url(self, envelope_id: str, nota) -> str:
        """Gera URL para assinatura do sacado após a assinatura do cedente"""
        try:
            status_info = self.get_envelope_status(envelope_id)
            
            if status_info['cedente_status'] != 'completed':
                print("O cedente ainda não assinou o documento. A URL do sacado não pode ser gerada.")
                
            url_assinatura_sacado = self.get_embedded_signing_url(
                envelope_id=envelope_id,
                signer_email=nota.email_sacado,
                signer_name=nota.sacado,
                recipient_id='2'
            )
        
            print("** Chamada ao microsserviço de email **")
            print(f"Para: {nota.email_sacado}")
            print("Assunto: Documento pendente de assinatura")
            print(f"URL: {url_assinatura_sacado}")

            return url_assinatura_sacado
        except ApiException as e:
            print(f"Erro ao gerar URL de assinatura para sacado: {str(e)}")
            raise
        except Exception as e:
            print(f"Erro na validação: {str(e)}")
            raise