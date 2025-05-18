import os
import sys
import time

os.environ["TZ"] = "America/Sao_Paulo"

try:
    time.tzset()  # Tenta aplicar a mudança de fuso horário em sistemas Unix-like
except:
    pass  # Ignora o erro em sistemas Windows

import logging
from flask import Flask, g, request, jsonify
from flask_cors import CORS
from sqlalchemy.pool import QueuePool
from authlib.integrations.flask_client import OAuth

from app.config import Config
from app.extensions.redis import init_redis
from app.extensions.database import db  
from app.extensions.cognito_auth import Cognito
from app.extensions.cognito_idp import CognitoIDP
from app.extensions.migrate import init_migrate
from app.extensions.restx_api import blueprint as api_blueprint


def register_logger():
    # Cria o logger principal
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Formato padrão para os logs
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
    )

    # Handler para exibir logs no console (como um "print")
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Verifica o ambiente
    app_env = os.getenv("APP_ENVIRONMENT", "production")

    if app_env == "local":
        # Handler para arquivo de INFO e superiores
        info_handler = logging.FileHandler("info.log")
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)

        # Handler para arquivo de ERROR e superiores
        error_handler = logging.FileHandler("error.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        # Adiciona os handlers de arquivo ao logger
        logger.addHandler(info_handler)
        logger.addHandler(error_handler)

    return logger


def register_blueprint(app):
    try:
        from app.routes import (
            tenant_route,
            config_route,
            home_route,
            fornecedor_route,
            usuario_route,
            fornecedor_nota_route,
            parceiro_route,
            auth_route,
            upload_route,
            fornecedor_parceiro_route,
            assinatura_contrato_fornecedor_route,
            assinatura_termo_de_uso_route,
            api_docs,
            support,
            cronjob_route,
            fornecedor_nota_parcela_route,
            webhook_route,
            form_link_route,
            form_webhook_route,
            fornecedor_pre_cadastro_route
        )
        # Register each blueprint with logging
        blueprints = [
            (tenant_route.tenant_bp, "tenant"),
            (config_route.config_bp, "config"),
            (home_route.home_bp, "home"),
            (auth_route.auth_bp, "auth"),
            (usuario_route.usuario_bp, "usuario"),
            (fornecedor_route.fornecedor_bp, "fornecedor"),
            (parceiro_route.parceiro_bp, "parceiro"),
            (fornecedor_nota_route.fornecedor_nota_bp, "fornecedor_nota"),
            (fornecedor_nota_parcela_route.fornecedor_nota_parcela_bp, "fornecedor_nota_parcela"),
            (upload_route.upload_bp, "upload"),
            (assinatura_contrato_fornecedor_route.assinatura_contrato_bp, "assinatura_contrato"),
            (assinatura_termo_de_uso_route.assinatura_termo_bp, "assinatura_termo"),
            (fornecedor_parceiro_route.fornecedor_parceiro_bp, "fornecedor_parceiro"),
            (api_docs.api_docs_bp, "api_docs"),
            (support.support_bp, "support"),
            (form_link_route.form_link_bp, "form_link"),
            (fornecedor_pre_cadastro_route.bp, "fornecedor_pre_cadastro")
        ]

        # Registra as blueprints padrão com prefixo /api
        for blueprint, name in blueprints:
            try:
                app.register_blueprint(blueprint, url_prefix="/api")
            except Exception as e:
                app.logger.error(f"Error registering {name} blueprint: {str(e)}")
                raise

        # Registra a blueprint do cronjob separadamente com prefixo específico
        try:
            app.register_blueprint(cronjob_route.cronjob_bp, url_prefix="/api/cronjob")
            app.logger.info("Cronjob blueprint registered successfully")
        except Exception as e:
            app.logger.error(f"Error registering cronjob blueprint: {str(e)}")
            raise
        # Registra a blueprint do cronjob separadamente com prefixo específico
        try:
            app.register_blueprint(webhook_route.webhook_bp, url_prefix="/api/webhook")
            app.logger.info("Webhook blueprint registered successfully")
        except Exception as e:
            app.logger.error(f"Error registering webhook blueprint: {str(e)}")
            raise

        # Register the form webhook blueprint with specific prefix (public route)
        try:
            app.register_blueprint(form_webhook_route.form_webhook_bp, url_prefix="/api/form")
            app.logger.info("Form webhook blueprint registered successfully")
        except Exception as e:
            app.logger.error(f"Error registering form webhook blueprint: {str(e)}")
            raise

        app.logger.info("All blueprints registered successfully")
        return app

    except Exception as e:
        app.logger.error(f"Error in blueprint registration: {str(e)}")
        app.logger.error(f"Error traceback:", exc_info=True)
        raise


def create_app(config=Config):
    app = Flask(__name__, template_folder="./templates")
    CORS(app)
    app.secret_key = os.getenv("FLASK_SECRET")
    app.config.from_object(config)
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 20,
        "max_overflow": 0,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "poolclass": QueuePool,
    }

    app.logger = register_logger()

    app.config['DEPENDENCIES_LOADED'] = False

    try:
        ## INIT REDIS
        init_redis(app)
    except Exception as e:
        app.logger.error(f"Erro ao iniciar o Redis: {str(e)}")

    try:
        ## INIT DATABASE
        db.init_app(app)
    except Exception as e:
        app.logger.error(f"Erro ao iniciar o banco de dados: {str(e)}")
    
    try:
        init_migrate(app, db)
    except Exception as e:
        app.logger.error(f"Erro ao iniciar o Migrate: {str(e)}")

    try:
        from app.models.config_model import ConfigModel
        from app.models.fornecedor_model import Fornecedor
        from app.models.parceiro_model import Parceiro
        from app.models.fornecedor_parceiro_model import FornecedorParceiro
        from app.models.usuario_model import Usuario
        from app.models.quadro_alerta_model import QuadroAlerta
        from app.models.fornecedor_nota_model import FornecedorNota
        from app.models.status_nota import StatusNota
        from app.models.status_nota_admin import StatusNotaAdmin
        from app.models.assinatura_contrato_fornecedor_model import (
            AssinaturaContratoFornecedor
        )
        from app.models.assinatura_termo_de_uso_model import AssinaturaTermoDeUso
        from app.models.assinatura_nota_model import AssinaturaNota
        from app.models.assinatura_upload import AssinaturaUpload
        from app.models.agendamento_model import Agendamento, AgendamentoHistorico
        from app.models.assinatura_nota_resumo_model import AssinaturaNotaResumo
        from app.models.fornecedor_nota_parcela_model import FornecedorNotaParcela
        from app.models.status_nota_parcela_model import StatusNotaParcela
        from app.models.status_nota_parcela_admin_model import StatusNotaParcelaAdmin
    except Exception as e:
        app.logger.error(f"Erro ao importar modelos: {str(e)}")
        # raise Exception(f"Erro ao importar modelos: {str(e)}")

    try:
        # Configuração OAuth com Authlib
        oauth = OAuth(app)
        app.config['DEPENDENCIES_LOADED'] = True
        app.config['OAUTH'] = oauth
    except Exception as e:
        app.logger.error(f"Erro ao configurar o OAuth: {str(e)}")
        # raise Exception(f"Erro ao configurar o OAuth: {str(e)}")

    @app.before_request
    def check_dependencies():
        if request.endpoint == "ping" or request.endpoint == "api/ping":
            return  # Ignora verificação para endpoints de health check
        
        if not app.config.get('DEPENDENCIES_LOADED', False):
            app.logger.error("Tentativa de acessar rota com dependências não carregadas")

    @app.before_request
    def initiate_cognito():
        if request.endpoint == "ping" or request.endpoint == "api/ping":
            return  # Ignora o processamento para o endpoint de health check
        
        if not app.config.get('DEPENDENCIES_LOADED', False):
            return  # Não executa se as dependências não foram carregadas
            
        try:
            oauth = app.config.get('OAUTH')
            g.cognito = Cognito(oauth)  # Usa a instância de aplicação do Cognito
            # Instancia o CognitoIDP por usuário (por requisição)
            g.cognito_idp = CognitoIDP(g.cognito)
        except Exception as e:
            app.logger.error(f"Erro ao iniciar o CognitoIDP: {str(e)}")

    @app.before_request
    def get_full_domain():
        if request.endpoint == "ping" or request.endpoint == "api/ping":
            return  # Ignora o processamento para o endpoint de health check
        
        if not app.config.get('DEPENDENCIES_LOADED', False):
            return  # Não executa se as dependências não foram carregadas
            
        # Extrai o domínio completo (sem caminho)
        full_domain = request.host.split(":")[0]  # Remove a porta, se presente
        # Armazena o domínio no objeto global 'g'
        g.full_domain = full_domain
        

    @app.before_request
    def get_tenant():
        if request.endpoint == "ping" or request.endpoint == "api/ping":
            return  # Ignora o processamento para o endpoint de health check
        
        if not app.config.get('DEPENDENCIES_LOADED', False):
            return  # Não executa se as dependências não foram carregadas
        
        # Verifica se a variável de ambiente LOCAL_EXECUTING existe
        if os.getenv("LOCAL_EXECUTING"):
            # Se existir, define o tenant como "aeco"
            tenant = "aeco"
        else:
            # Extrai o tenant do subdomínio como antes
            host_parts = request.host.split(".")
            tenant = host_parts[0] if len(host_parts) > 0 else "default"
            
        g.tenant_url = tenant  # Armazena o tenant no objeto global 'g'

    # Só registra as blueprints se as dependências foram carregadas
    if app.config.get('DEPENDENCIES_LOADED', False):
        try:
            register_blueprint(app)
        except Exception as e:
            app.logger.error(f"Erro na definição das blueprints: {str(e)}")
            app.config['DEPENDENCIES_LOADED'] = False

    @app.route("/api/ping", methods=["GET"])
    def ping():
        return jsonify({"pong": True})

    # Register the API blueprint
    if app.config.get('DEPENDENCIES_LOADED', False):
        app.register_blueprint(api_blueprint)

    return app
