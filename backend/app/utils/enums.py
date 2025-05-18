LINK_PORTAL = "https://%s.riscosacado.aeco.app.br/"

meses = {
    1: 'janeiro',
    2: 'fevereiro',
    3: 'março',
    4: 'abril',
    5: 'maio',
    6: 'junho',
    7: 'julho',
    8: 'agosto',
    9: 'setembro',
    10: 'outubro',
    11: 'novembro',
    12: 'dezembro'
}

AGENDAMENTOS_PADRAO = [
    {
        "nome": "E-mail Notas Disponíveis",
        "tipo_tarefa": "email_nota_disponivel",
        "excluido": 1
    },
    {
        "nome": "Expiração Automática de Notas",
        "tipo_tarefa": "expiracao_nota",
        "excluido": 0
    },
    {
        "nome": "Atualização Automática de Valores de Notas",
        "tipo_tarefa": "calcula_nota",
        "excluido": 0
    },
    {
        "nome": "Habilitar Fornecedores Automaticamente",
        "tipo_tarefa": "habilitar_fornecedor_auto",
        "excluido": 1
    },
    {
        "nome": "E-mail Arquivo Retorno Automático",
        "tipo_tarefa": "habilitar_retorno_auto",
        "excluido": 1
    },
    {
        "nome": "Notificação de Cadastro Incompleto",
        "tipo_tarefa": "notificacao_cadastro_incompleto",
        "excluido": 1
    },
    {
        "nome": "Notificação de notas próximas de expirar",
        "tipo_tarefa": "notificacao_nota_expirar_auto",
        "excluido": 1
    }
]