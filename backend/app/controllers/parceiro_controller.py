# app/controllers/parceiro_controller.py
from app.services.parceiro_service import ParceiroService
from app.utils.paginacao import PaginacaoHelper
from flask import jsonify, g
from app.services.config_tenant_service import ConfigTenantService
from app.services.agendamento_service import AgendamentoService
from app.utils.enums import AGENDAMENTOS_PADRAO

class ParceiroController():
    @staticmethod
    def home():
        tenant_code = g.tenant_url
        dashboard_data = ParceiroService.get_dashboard_data(tenant_code)
        if not dashboard_data:
            return "Parceiro não encontrado", 404

        return jsonify(dashboard_data), 200

    # CREATE
    @staticmethod
    def create_parceiro(dados):
        try:
            parceiro = ParceiroService.create_parceiro(dados) 
        except Exception as e:
            return {"msg": "Erro ao criar parceiro", "error": str(e)}, 400
        
        if not parceiro:
            return {"msg": "Erro ao criar parceiro"}, 400
        
        # Criar config
        try:
            config_service = ConfigTenantService()     
            config_data = {
                'parceiro_id': parceiro.id,
                'prazo_maximo': 120,
                'dias_ate_vencimento': 10,
            }   
            config = config_service.create_config(config_data)
        except Exception as e:
            return {"msg": "Erro ao criar config", "error": str(e)}, 400
        
        try:
            agendamento_service = AgendamentoService()
            for agendamento in AGENDAMENTOS_PADRAO:
                try:
                    agendamento_data = {
                        **agendamento,
                        'parceiro_id': parceiro.id,
                        'config_id': config.id
                    }
                    agendamento_service.create_agendamento(agendamento_data)
                except Exception as e:
                    return {"msg": f"Erro ao criar agendamento {agendamento['nome']}", "error": str(e)}, 400
        except Exception as e:
            return {"msg": "Erro ao criar agendamento", "error": str(e)}, 400

        return parceiro
    
    # UPDATE
    @staticmethod
    def update_parceiro(parceiro_id, dados):
        return ParceiroService.update_parceiro(parceiro_id, dados)
    
    @staticmethod
    def delete_parceiro(parceiro_id):
        try:
            # Deletar agendamentos
            agendamento_service = AgendamentoService()
            agendamentos = agendamento_service.get_agendamentos_by_parceiro(parceiro_id)
            for agendamento in agendamentos:
                agendamento_service.delete_agendamento(agendamento.id)

            # Deletar config
            config_service = ConfigTenantService()
            config = config_service.get_config_by_parceiro_id(parceiro_id)
            if config:
                config_service.delete_config(config['id'])

            # Deletar parceiro
            resultado = ParceiroService.delete_parceiro(parceiro_id)
            if not resultado:
                return False, "Erro ao deletar parceiro"

            return True, "Parceiro deletado com sucesso"
            
        except Exception as e:
            return False, f"Erro ao deletar parceiro {e}"
    ## GET
    @staticmethod
    def get_all_parceiro(page, per_page):
        query = ParceiroService.get_all_parceiro()
        return PaginacaoHelper.paginate_query(
            query,
            page,
            per_page
        )
    
    @staticmethod
    def get_parceiro_por_id(parceiro_id):
        return ParceiroService.get_parceiro_por_id(parceiro_id)
    @staticmethod
    def get_parceiro_por_tenant(tenant):
        return ParceiroService.get_parceiro_por_tenant(tenant)
