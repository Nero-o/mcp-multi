from app.repositories.agendamento_repository import AgendamentoRepository

class AgendamentoService:
    def __init__(self):
        self.repository = AgendamentoRepository()

    def create_agendamento(self, dados):
        agendamento_data = {
            'nome': dados.get('nome'),
            'tipo_tarefa': dados.get('tipo_tarefa'),
            'hora': dados.get('hora', '00:00'),  # valor padrão
            'dia_semana': dados.get('dia_semana', '0'),  # valor padrão
            'excluido': dados.get('excluido', True),
            'parceiro_id': dados.get('parceiro_id'),
            'config_id': dados.get('config_id'),
            'parametros': dados.get('parametros')
        }
        
        return self.repository.create(agendamento_data)

    def get_agendamento(self, agendamento_id):
        return self.repository.get_by_id(agendamento_id)

    def get_agendamentos_by_parceiro(self, parceiro_id):
        return self.repository.get_by_parceiro_id(parceiro_id)
    
    def delete_agendamento(self, agendamento_id):
        return self.repository.delete(agendamento_id)

