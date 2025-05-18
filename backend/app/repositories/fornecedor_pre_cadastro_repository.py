from app.models.fornecedor_pre_cadastro_model import FornecedorPreCadastro
from app.extensions.database import db
from flask import current_app

class FornecedorPreCadastroRepository:
    @staticmethod
    def create_pre_cadastro(data: dict) -> FornecedorPreCadastro:
        try:
            current_app.logger.info("Iniciando criação de registro no banco de dados")
            pre_cadastro = FornecedorPreCadastro(**data)
            db.session.add(pre_cadastro)
            db.session.commit()
            current_app.logger.info(f"Registro criado com sucesso. ID: {pre_cadastro.id}")
            return pre_cadastro
        except Exception as e:
            current_app.logger.error(f"Erro ao criar registro no banco de dados: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def get_pre_cadastro_by_id(id: int) -> FornecedorPreCadastro:
        current_app.logger.info(f"Buscando pré-cadastro por ID: {id}")
        return FornecedorPreCadastro.query.get(id)

    @staticmethod
    def get_pre_cadastro_by_cpf_cnpj(cpf_cnpj: str) -> FornecedorPreCadastro:
        current_app.logger.info(f"Buscando pré-cadastro por CPF/CNPJ: {cpf_cnpj}")
        return FornecedorPreCadastro.query.filter_by(cpf_cnpj=cpf_cnpj).first()

    @staticmethod
    def update_pre_cadastro(id: int, data: dict) -> FornecedorPreCadastro:
        try:
            current_app.logger.info(f"Iniciando atualização do pré-cadastro ID: {id}")
            pre_cadastro = FornecedorPreCadastro.query.get(id)
            if pre_cadastro:
                for key, value in data.items():
                    setattr(pre_cadastro, key, value)
                db.session.commit()
                current_app.logger.info(f"Pré-cadastro ID: {id} atualizado com sucesso")
            else:
                current_app.logger.warning(f"Pré-cadastro ID: {id} não encontrado para atualização")
            return pre_cadastro
        except Exception as e:
            current_app.logger.error(f"Erro ao atualizar pré-cadastro ID: {id}: {str(e)}")
            db.session.rollback()
            raise