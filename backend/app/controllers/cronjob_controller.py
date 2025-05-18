from app.extensions.lambda_invoke import MessageProcessor
from app.controllers.parceiro_controller import ParceiroController
from app.services.agendamento_service import AgendamentoService
from flask import jsonify

class CronjobController:
    def __init__(self):
        self.agendamento_service = AgendamentoService()
        self.message_processor = MessageProcessor()  # Nova instância

    def executar_task_cronjob(self, tipo_task, tenant_url):
        try:
            parceiro = ParceiroController.get_parceiro_por_tenant(tenant_url)
            if not parceiro:
                return jsonify({'message': 'Parceiro não encontrado.'}), 404

            task = self._get_task(parceiro.id, tipo_task)
            if isinstance(task, tuple):
                return task

            return self._executar_lambda(task)
        
        except Exception as e:
            return jsonify({'message': f'Erro ao executar tarefa {tipo_task}: {e}'}), 500

    def _get_task(self, parceiro_id, tipo_task):
        agendamentos = self.agendamento_service.get_agendamentos_by_parceiro(parceiro_id)
        if not agendamentos:
            return jsonify({'message': 'Nenhum agendamento encontrado.'}), 404

        task_list = self._filtrar_agendamentos(agendamentos, tipo_task)
        if not task_list:
            return jsonify({
                'message': f'Nenhum agendamento encontrado para a tarefa {tipo_task}.'
            }), 404

        return task_list[0]

    def _filtrar_agendamentos(self, agendamentos, tipo_task):
        return [agendamento for agendamento in agendamentos if agendamento.tipo_tarefa == tipo_task]

    def _executar_lambda(self, task):
        try:
            self.message_processor.send_to_queue(
                tipo_tarefa=task.tipo_tarefa,
                agendamento_id=task.id,
                parceiro_id=task.parceiro_id,
                parametros=None
            )
            return jsonify({
                'message': f'Tarefa {task.tipo_tarefa} enviada para fila com sucesso'
            }), 200
        except Exception as e:
            print(f'Erro ao enviar tarefa {task.tipo_tarefa} para fila: {e}.')
            return jsonify({
                'message': f'Erro ao enviar tarefa {task.tipo_tarefa} para fila: {e}.'
            }), 400
