import re
from datetime import datetime


def formata_valores_financeiros(nota):
    if nota:
        try:
            nota.vlr_face = float(nota.vlr_face)
            nota.vlr_disp_antec = float(nota.vlr_disp_antec)
        except Exception as e:
            print(f"Erro ao formatar valores financeiros: {e}")
    return nota


def replace_empty_strings_with_none(data_dict):
    for key, value in data_dict.items():
        if isinstance(value, dict):
            replace_empty_strings_with_none(value)
        elif value == "" or value == "None":
            data_dict[key] = None
    return data_dict


def remove_special_characters(number_str):
    if number_str is None:
        return None
    return re.sub(r"[^0-9]", "", number_str)


def apply_phone_mask(phone_str):
    if phone_str:
        phone_str = re.sub(r"\D", "", phone_str)  # Remove caracteres não numéricos
        if len(phone_str) == 10:  # Telefone residencial
            return "({}) {}-{}".format(phone_str[:2], phone_str[2:6], phone_str[6:])
        elif len(phone_str) == 11:  # Telefone celular
            return "({}) {}-{}".format(phone_str[:2], phone_str[2:7], phone_str[7:])
    return phone_str


def apply_cpf_mask(cpf_str):
    if cpf_str and len(cpf_str) == 11:
        return "{}.{}.{}-{}".format(
            cpf_str[:3], cpf_str[3:6], cpf_str[6:9], cpf_str[9:]
        )
    return cpf_str


def apply_cnpj_mask(cnpj_str):
    if cnpj_str and len(cnpj_str) == 14:
        return "{}.{}.{}/{}-{}".format(
            cnpj_str[:2], cnpj_str[2:5], cnpj_str[5:8], cnpj_str[8:12], cnpj_str[12:]
        )
    return cnpj_str


def format_cpf_cnpj(number_str):
    if number_str is None:
        return None
    number_str = remove_special_characters(number_str)
    if len(number_str) == 11:
        return apply_cpf_mask(number_str)
    elif len(number_str) == 14:
        return apply_cnpj_mask(number_str)
    else:
        return number_str


def force_str_to_date_obj(date_str, formats=None):
    if not formats:
        formats = ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y")
    if isinstance(date_str, str) and date_str != "":
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt).date()
                return date_obj
            except ValueError:
                continue
        raise ValueError(f"Formato de data inválido: {date_str}")
    elif isinstance(date_str, datetime):
        return date_str.date()
    else:
        return date_str
