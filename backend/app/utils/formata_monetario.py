def formata_monetario(valor, separador_milhar, separador_decimal):
    # Primeiro, formatamos o valor com duas casas decimais
    valor_str = f"{valor:.2f}"
    # Separamos a parte inteira da parte decimal
    parte_inteira, parte_decimal = valor_str.split('.')
    # Adicionamos o separador de milhar, se necessário
    if separador_milhar:
        # Invertimos a string para facilitar a inserção do separador a cada 3 dígitos
        parte_inteira_reversa = parte_inteira[::-1]
        # Agrupamos os dígitos em grupos de três
        grupos = [parte_inteira_reversa[i:i+3] for i in range(0, len(parte_inteira_reversa), 3)]
        # Definimos o separador de milhar com base no separador decimal
        if separador_decimal == ',':
            separador_milhar_char = '.'
        else:
            separador_milhar_char = ','
        # Juntamos os grupos com o separador de milhar
        parte_inteira_formatada = separador_milhar_char.join(grupos)
        # Revertimos novamente para a ordem correta
        parte_inteira = parte_inteira_formatada[::-1]
    # Juntamos a parte inteira e decimal com o separador decimal
    valor_formatado = parte_inteira + separador_decimal + parte_decimal
    return valor_formatado

def formata_float_para_moeda(valor_float):
    if valor_float is None:
        return "R$ 0,00"
    return f"R$ {valor_float:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')