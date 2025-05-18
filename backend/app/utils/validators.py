# backend/app/utils/validators.py
import re

def validate_cpf(cpf: str) -> bool:
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Validação do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10 % 11) % 10
    if int(cpf[9]) != digito1:
        return False
    
    # Validação do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10 % 11) % 10
    if int(cpf[10]) != digito2:
        return False
    
    return True

def validate_cnpj(cnpj: str) -> bool:
    # Remove caracteres não numéricos
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    if len(cnpj) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False
    
    # Validação do primeiro dígito verificador
    soma = sum(int(cnpj[i]) * (5 - i) for i in range(4))
    soma += sum(int(cnpj[i]) * (9 - i) for i in range(4, 12))
    digito1 = (soma * 10 % 11) % 10
    if int(cnpj[12]) != digito1:
        return False
    
    # Validação do segundo dígito verificador
    soma = sum(int(cnpj[i]) * (6 - i) for i in range(5))
    soma += sum(int(cnpj[i]) * (9 - i) for i in range(5, 13))
    digito2 = (soma * 10 % 11) % 10
    if int(cnpj[13]) != digito2:
        return False
    
    return True

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    # Remove caracteres não numéricos
    phone = re.sub(r'[^0-9]', '', phone)
    
    # Verifica se tem entre 10 e 11 dígitos (com DDD)
    return 10 <= len(phone) <= 11