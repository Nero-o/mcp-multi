from flask_migrate import Migrate

migrate = Migrate()

def init_migrate(app, db):
    try:
        # Inicializa o Flask-Migrate com a aplicação e a instância do banco de dados
        migrate.init_app(app, db)
        app.logger.info("Migrate inicializado com sucesso")
        
    except Exception as e:
        app.logger.error(f"Erro ao inicializar o Migrate: {str(e)}")