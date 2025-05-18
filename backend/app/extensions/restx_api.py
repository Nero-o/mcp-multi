from flask_restx import Api
from flask import Blueprint
import logging

logger = logging.getLogger(__name__)

try:
    
    # Create blueprint
    blueprint = Blueprint('api', __name__, url_prefix='/api')

    # Initialize API
    api = Api(
        blueprint,
        title='AECO Risco Sacado API',
        version='1.0',
        description='API Documentation for Aeco Risco Sacado',
        doc='/docs',
        authorizations={
            'apikey': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization'
            }
        },
        swagger_ui_bundle_js='https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js',
        swagger_ui_standalone_preset_js='https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-standalone-preset.js',
        swagger_ui_css='https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css',
        template={
            'swagger_ui_css': lambda: (
                '''
                .swagger-ui .wrapper {
                    padding: 0;
                    max-width: none;
                }
                .swagger-ui .opblock-body {
                    max-height: none;
                }
                .swagger-ui .opblock-body pre {
                    max-height: 400px;
                    overflow-y: auto;
                }
                .swagger-ui {
                    overflow-y: auto;
                    height: calc(100vh - 100px);
                }
                '''
            )
        }
    )

except Exception as e:
    logger.error(f"Error initializing REST-X API: {str(e)}")
    logger.error("Error traceback:", exc_info=True)
    raise

# # Log namespaces when they are added
# def log_namespace(namespace):
#     logger.info(f"Registering namespace: {namespace.name} at path {namespace.path}")

# Monkey patch the add_namespace method to log when namespaces are added
original_add_namespace = api.add_namespace
def add_namespace_with_logging(self, ns, *args, **kwargs):
    # log_namespace(ns)
    original_add_namespace(ns, *args, **kwargs)
api.add_namespace = lambda ns, *args, **kwargs: add_namespace_with_logging(api, ns, *args, **kwargs) 