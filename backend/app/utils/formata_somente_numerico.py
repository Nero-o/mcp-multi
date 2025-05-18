import re 

def formata_somente_numerico(str_to_number):
    return re.sub(r'\D', '', str_to_number) 