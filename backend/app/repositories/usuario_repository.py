from app.models.usuario_model import Usuario
from app.models.parceiro_model import Parceiro
from app.extensions.database import db
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

class UsuarioRepository:
    
    @staticmethod
    def update_usuario_por_idp_user_id(idpUserId, dados):
        usuario = Usuario.query.filter_by(idpUserId=idpUserId).first()
        if usuario:
            for key, value in dados.items():
                setattr(usuario, key, value)
            db.session.commit()
        return usuario

    @staticmethod    
    def get_all_usuario():
        query =  Usuario.query
        query = query.join(Parceiro, Usuario.parceiro_id == Parceiro.id) \
            .add_columns(Parceiro.nome, Parceiro.tenant_code)
        return query

    @staticmethod
    def create_usuario(dados):
        try:
            novo_usuario = Usuario(**dados)
            db.session.add(novo_usuario)
            db.session.commit()
            return novo_usuario
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao criar usuário no banco de dados: {str(e)}")
            raise e
    
    @staticmethod
    def find_columns_db(dados):
        colunas_usuario_db = Usuario.__table__.columns
        dados_db = {}

        for col in colunas_usuario_db:
            if col.name in dados:
                dados_db[col.name] = dados[col.name]

        return dados_db
    

    
    @staticmethod
    def get_usuario_por_campos(campos):
        try:
            return Usuario.query.filter_by(**campos).first()
        except Exception as e:
            raise e
        
    @staticmethod
    def get_usuario_por_fornecedor_parceiro(fornecedor_id, parceiro_id):
        return Usuario.query.filter_by(
            fornecedor_id=fornecedor_id,
            parceiro_id=parceiro_id
        ).first()
    
    # READ
    @staticmethod
    def get_all_usuarios():
        return Usuario.query.all()
    
    @staticmethod
    def get_usuario_por_id(usuario_id):
        return Usuario.query.get(usuario_id)
    
    @staticmethod
    def get_usuario_por_username(username, parceiro_id=None):
        query = Usuario.query.filter_by(idpUserId=username)
        if parceiro_id:
            query = query.filter_by(parceiro_id=parceiro_id)
        return query
    
    # UPDATE
    @staticmethod
    def update_usuario(usuario_id, dados):
        usuario = UsuarioRepository.get_usuario_por_id(usuario_id)
        if usuario:
            for key, value in dados.items():
                setattr(usuario, key, value)
            db.session.commit()
        return usuario

    # DELETE
    @staticmethod
    def delete_usuario(usuario_id):
        usuario = Usuario.query.get(usuario_id)
        if usuario:
            db.session.delete(usuario)
            db.session.commit()
            return True
        return False
