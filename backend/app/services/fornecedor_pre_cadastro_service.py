from app.repositories.fornecedor_pre_cadastro_repository import FornecedorPreCadastroRepository
from app.utils.validators import validate_email, validate_phone
from flask import current_app

class FornecedorPreCadastroService:
    def __init__(self):
        self.repository = FornecedorPreCadastroRepository()

    def create_pre_cadastro(self, data: dict) -> dict:
        current_app.logger.info(f"Iniciando criação de pré-cadastro para CNPJ: {data.get('cpf_cnpj')}")
        
        required_fields = [
            'razao_social',
            'nome_fantasia',
            'cpf_cnpj',
            'email',
            'telefone',
            'nome_representante',
            'cpf_representante',
            'email_representante',
            'endereco',
            'complemento',
            'cidade',
            'estado',
            'cep',
            'pais',
            'fonte_conhecimento'
        ]

        # Verifica campos obrigatórios
        for field in required_fields:
            if not data.get(field):
                current_app.logger.error(f"Campo obrigatório ausente: {field}")
                raise ValueError(f"O campo {field.replace('_', ' ').title()} é obrigatório")

        # Validações específicas
        if not (data['cpf_cnpj']):
            current_app.logger.error(f"CNPJ inválido: {data['cpf_cnpj']}")
            raise ValueError("CNPJ inválido")
        
        if not (data['cpf_representante']):
            current_app.logger.error(f"CPF do representante inválido: {data['cpf_representante']}")
            raise ValueError("CPF do representante inválido")
        
        if not validate_email(data['email']):
            current_app.logger.error(f"Email inválido: {data['email']}")
            raise ValueError("Email inválido")
        
        if not validate_email(data['email_representante']):
            current_app.logger.error(f"Email do representante inválido: {data['email_representante']}")
            raise ValueError("Email do representante inválido")
        
        if not validate_phone(data['telefone']):
            current_app.logger.error(f"Telefone inválido: {data['telefone']}")
            raise ValueError("Telefone inválido")

        # Verifica se já existe um pré-cadastro com o mesmo CNPJ
        existing = self.repository.get_pre_cadastro_by_cpf_cnpj(data['cpf_cnpj'])
        if existing:
            current_app.logger.warning(f"Tentativa de cadastro com CNPJ já existente: {data['cpf_cnpj']}")
            raise ValueError("Já existe um pré-cadastro com este CNPJ")

        try:
            pre_cadastro = self.repository.create_pre_cadastro(data)
            current_app.logger.info(f"Pré-cadastro criado com sucesso. ID: {pre_cadastro.id}")
            
            return {
                'id': pre_cadastro.id,
                'razao_social': pre_cadastro.razao_social,
                'cpf_cnpj': pre_cadastro.cpf_cnpj,
                'status': pre_cadastro.status,
                'data_pre_cadastro': pre_cadastro.data_pre_cadastro.isoformat()
            }
        except Exception as e:
            current_app.logger.error(f"Erro ao criar pré-cadastro: {str(e)}")
            raise