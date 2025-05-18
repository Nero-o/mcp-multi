from flask import current_app, g
from datetime import datetime
from app.repositories.usuario_repository import UsuarioRepository
from app.services.cognito_service import CognitoService
from app.models.fornecedor_model import Fornecedor
from app.models.fornecedor_parceiro_model import FornecedorParceiro
from app.extensions.database import db
from app.utils.helpers import replace_empty_strings_with_none, format_cpf_cnpj, apply_phone_mask
from app.utils.senha_temporaria import gerar_senha_temporaria



class UsuarioService():

    @staticmethod
    def update_usuario_por_idp_user_id(idpUserId, dados):
        return UsuarioRepository.update_usuario_por_idp_user_id(idpUserId, dados)

    @staticmethod
    def get_all_usuario():
        return UsuarioRepository.get_all_usuario()

    @staticmethod
    def get_usuario_por_fornecedor_parceiro(fornecedor_id, parceiro_id):
        return UsuarioRepository.get_usuario_por_fornecedor_parceiro(fornecedor_id, parceiro_id)

    @staticmethod
    def get_usuario_por_username(username, parceiro_id=None): 
        return UsuarioRepository.get_usuario_por_username(username, parceiro_id).all()
    
    @staticmethod
    def get_usuario_por_id(usuario_id):
        return UsuarioRepository.get_usuario_por_id(usuario_id)

    # UPDATE
    @staticmethod
    def update_usuario(usuario_id, dados):
        return UsuarioRepository.update_usuario(usuario_id, dados)

    # DELETE
    @staticmethod
    def delete_usuario(usuario_id):
        usuario = UsuarioRepository.get_usuario_por_id(usuario_id)

        if not usuario:
            return False

        username = usuario.serialize()['idpUserId']

        try:
            UsuarioRepository.delete_usuario(usuario_id)
            CognitoService.delete_user(username)
        except Exception as e:
            current_app.logger.error(f"Erro ao deletar o usuario no banco de dados: {str(e)}")
            raise e

        return True

    @staticmethod
    def create_usuario(dados):
        if not all(key in dados for key in ['username', 'role', 'email']):
            return ('Dados inválidos. Username, role e email são obrigatórios.', False)

        try:
            # Se for um fornecedor, processa primeiro o fornecedor
            if 'Fornecedor' in dados['role']:
                dados = UsuarioService._formata_campos_fornecedor(dados)
                fornecedor = UsuarioService._processa_fornecedor(dados)
                if not fornecedor:
                    return ('Erro ao processar fornecedor.', False)
                
                dados['fornecedor_id'] = fornecedor.id

            # Processa usuário no Cognito
            usuario_cognito, senha_temporaria = UsuarioService._get_or_create_user_cognito(dados)
            
            if not usuario_cognito:
                return ('Erro ao criar/obter usuário no Cognito.', False)

            # Extrai o ID do Cognito
            cognito_id_usuario = (usuario_cognito.get('User', {}) or usuario_cognito).get('Username')
            if not cognito_id_usuario:
                return ('Não foi possível recuperar o ID do usuário Cognito.', False)

            # Verifica vínculo com parceiro
            if 'Parceiro' in dados['role']:
                usuario_existente = UsuarioRepository.get_usuario_por_username(
                    cognito_id_usuario, 
                    dados['parceiro_id'] 
                ).first()
                
                if usuario_existente:
                    return ('Usuário já cadastrado para o parceiro selecionado.', False)

            # Prepara dados para o banco
            dados_usuario_db = {
                'idpUserId': dados['email'],
                'role': dados['role'],
                'parceiro_id': dados['parceiro_id'],
                'fornecedor_id': dados.get('fornecedor_id'),
                'senha_temporaria': senha_temporaria,
                'idpUserId': cognito_id_usuario,
                'excluido': False
            }

            # Cria usuário no banco
            try:
                usuario_db = UsuarioRepository.create_usuario(dados_usuario_db)
                db.session.commit()
                return usuario_db
            except Exception as e:
                current_app.logger.error(f"Erro ao criar usuário no banco: {str(e)}")
                db.session.rollback()
                return (f'Erro ao criar usuário no banco: {str(e)}', False)

        except Exception as e:
            current_app.logger.error(f"Erro ao criar usuário: {str(e)}")
            db.session.rollback()
            return (f'Erro ao criar usuário: {str(e)}', False)

    @staticmethod
    def _formata_campos_fornecedor(dados):
        """Formata campos específicos do fornecedor"""
        if "cpf_cnpj" in dados and dados["cpf_cnpj"]:
            dados["cpf_cnpj"] = format_cpf_cnpj(dados["cpf_cnpj"])

        for campo in ["bco", "agencia", "conta"]:
            if dados.get(campo) in ["0", 0]:
                dados[campo] = None

        if dados.get("telefone"):
            dados["telefone"] = apply_phone_mask(dados["telefone"])

        return replace_empty_strings_with_none(dados)

    @staticmethod
    def _get_or_create_user_cognito(dados):
        """Processa usuário no Cognito, similar ao processador-csv"""
        try:
            # Verifica se usuário já existe
            usuario_existente = CognitoService.get_user_by_email(dados['email'])
            if usuario_existente:
                usuario_db = UsuarioRepository.get_usuario_por_username(
                    usuario_existente.get('Username'),
                    dados['parceiro_id']
                ).first()
                senha_temporaria = usuario_db.senha_temporaria if usuario_db else gerar_senha_temporaria()
                return usuario_existente, senha_temporaria

            # Cria novo usuário
            senha_temporaria = gerar_senha_temporaria()
            atributos = [
                {'Name': 'email', 'Value': dados['email']},
                {'Name': 'email_verified', 'Value': 'true'}
            ]
            
            novo_usuario = CognitoService.admin_create_user(
                username=dados['email'],
                lista_atributos=atributos,
                senha_temporaria=senha_temporaria,
                envia_email=dados['role'] in ['Administrador', 'Parceiro']
            )

            if novo_usuario:
                CognitoService.admin_add_user_to_group(
                    novo_usuario['User']['Username'], 
                    dados['role']
                )

                return novo_usuario, senha_temporaria

            return None, None
    
        except Exception as e:
            current_app.logger.error(f"Erro ao processar usuário no Cognito: {str(e)}")
            raise

    @staticmethod
    def _get_or_create_user_banco(dados_usuario_db, usuario_cognito, senha_temporaria):
        """Processa usuário no banco de dados, similar ao processador-csv"""
        try:
            # Verifica se usuário já existe
            usuario_existente = UsuarioRepository.get_usuario_por_campos({
                'fornecedor_id': dados_usuario_db.get('fornecedor_id'),
                'parceiro_id': dados_usuario_db['parceiro_id'],
                'idpUserId': dados_usuario_db['idpUserId']
            })

            if usuario_existente:
                return usuario_existente, True
            
            # Cria novo usuário
            dados_usuario_db.update({
                'senha_temporaria': senha_temporaria,
                'excluido': False
            })

            # Remove o campo 'id' se existir
            dados_usuario_db.pop('id', None)
            # Cria novo usuário
            return UsuarioRepository.create_usuario(dados_usuario_db), False

        except Exception as e:
            current_app.logger.error(f"Erro ao processar usuário no banco: {str(e)}")
            raise


    @staticmethod
    def _processa_fornecedor(dados):
        """Processa o fornecedor no banco de dados"""
        try:
            # Define campos válidos para o fornecedor
            CAMPOS_FORNECEDOR = [
                "cpf_cnpj",
                "email",
                "razao_social",
                "bco",
                "telefone",
                "agencia",
                "conta",
                "municipio",
                "uf",
                "numero",
                "compl",
                "bairro",
                "cep"
            ]

            dados_fornecedor = {
                k: v for k, v in dados.items() 
                if k in CAMPOS_FORNECEDOR and v is not None
            }

            # Busca fornecedor existente
            fornecedor = (
                db.session.query(Fornecedor)
                .filter_by(cpf_cnpj=dados['cpf_cnpj'], email=dados['email'])
                .first()
            )

            if not fornecedor:
                # Cria novo fornecedor
                fornecedor = Fornecedor(**dados_fornecedor)
                db.session.add(fornecedor)
                db.session.flush()  # Garante que fornecedor.id seja gerado

            # Busca vínculo com parceiro
            fornecedor_parceiro = (
                db.session.query(FornecedorParceiro)
                .filter_by(fornecedor=fornecedor, parceiro_id=dados['parceiro_id'])
                .first()
            )

            if not fornecedor_parceiro:
                # Cria vínculo com parceiro
                fornecedor_parceiro = FornecedorParceiro(
                    fornecedor=fornecedor,
                    parceiro_id=dados['parceiro_id'],
                    excluido=True
                )
                db.session.add(fornecedor_parceiro)
                db.session.flush()
            else:
                # Atualiza dados do fornecedor existente
                COLUNAS_ATUALIZAVEIS = [
                    "razao_social",
                    "bco",
                    "telefone",
                    "agencia",
                    "conta",
                    "municipio",
                    "uf",
                    "numero",
                    "compl",
                    "bairro",
                    "cep",
                ]
                
                alterado = False
                fornecedor_dict = fornecedor.serialize()
                
                for key, value in dados.items():
                    if key in COLUNAS_ATUALIZAVEIS:
                        if value and str(fornecedor_dict.get(key)) != str(value):
                            alterado = True
                            current_app.logger.info(
                                f"Coluna {key} alterada no fornecedor ... Antes: {fornecedor_dict.get(key)} - Depois: {value}"
                            )
                            setattr(fornecedor, key, value)

                if alterado:
                    fornecedor.data_alteracao = datetime.now()
                    db.session.flush()

            return fornecedor

        except Exception as e:
            current_app.logger.error(f"Erro ao processar fornecedor: {str(e)}")
            db.session.rollback()
            raise