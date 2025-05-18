import random
import string


def gerar_senha_temporaria(tamanho=8):
    if tamanho < 4:
        raise ValueError("O tamanho mínimo para a senha é 4")

    # Define os conjuntos de caracteres
    letras_minusculas = string.ascii_lowercase
    letras_maiusculas = string.ascii_uppercase
    digitos = string.digits
    caracteres_especiais = "!@#$%^&*()-_=+"

    # Garante que cada tipo de caractere seja incluído
    senha = [
        random.choice(letras_minusculas),
        random.choice(letras_maiusculas),
        random.choice(digitos),
        random.choice(caracteres_especiais),
    ]

    # Preenche o restante da senha
    if tamanho > 4:
        todos_caracteres = (
            letras_minusculas + letras_maiusculas + digitos + caracteres_especiais
        )
        senha += random.choices(todos_caracteres, k=tamanho - 4)

    # Embaralha a lista para evitar padrões
    random.shuffle(senha)

    # Converte a lista em string
    return "".join(senha)
