import os
from app import create_app
import logging

logger = logging.getLogger(__name__)


try:
    app = create_app()
except Exception as e:    
    logger.error(f"Erro ao criar o app: {e}")
    raise e

if __name__ == "__main__":
    try:
        app.run(debug=False, port=os.getenv('FLASK_RUN_PORT'), host=os.getenv('FLASK_RUN_HOST'))
    except Exception as e:
        logger.error(f"Erro ao iniciar o servidor: {e}")